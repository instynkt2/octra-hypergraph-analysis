#!/usr/bin/env python3
"""Independent algebraic checker for Octra's Bulletproof-style backend.

Scope: verifies identities in the scalar field, independently of Octra's C++
scalar/group implementation. It does not prove Fiat-Shamir security, argument
of knowledge, generator independence, or implementation correctness.
"""
from __future__ import annotations
import argparse, json, random
from pathlib import Path

L = 2**252 + 27742317777372353535851937790883648493
RNG = random.Random(0x0C7A2026)

def inv(x):
    if x % L == 0:
        raise ZeroDivisionError
    return pow(x, L-2, L)

def addv(a,b):
    return [(x+y)%L for x,y in zip(a,b)]
def scalev(a,c):
    return [(x*c)%L for x in a]

def dot(a,b): return sum((x*y)%L for x,y in zip(a,b))%L

def basis(dim,i):
    v=[0]*dim; v[i]=1; return v

def msm(scalars, points):
    dim=len(points[0]) if points else 1
    out=[0]*dim
    for s,p in zip(scalars,points): out=addv(out,scalev(p,s))
    return out

def ipp_verification_scalars(ch):
    lg=len(ch); n=1<<lg
    uinv=[inv(u) for u in ch]
    s=[0]*n
    s[0]=1
    for u in uinv: s[0]=s[0]*u%L
    for i in range(1,n):
        k=i.bit_length()-1
        ci=lg-1-k
        s[i]=s[i^(1<<k)]*ch[ci]*ch[ci]%L
    return s

def ipp_trial(n):
    lg=(n.bit_length()-1)
    dim=2*n+1; qidx=2*n
    G=[basis(dim,i) for i in range(n)]
    H=[basis(dim,n+i) for i in range(n)]
    Q=basis(dim,qidx)
    a=[RNG.randrange(L) for _ in range(n)]
    b=[RNG.randrange(L) for _ in range(n)]
    P0=msm(a+b+[dot(a,b)],G+H+[Q])
    Ls=[]; Rs=[]; ch=[]
    aa=a[:]; bb=b[:]; GG=G[:]; HH=H[:]
    nn=n
    for _ in range(lg):
        half=nn//2
        cL=dot(aa[:half],bb[half:])
        cR=dot(aa[half:],bb[:half])
        LP=msm(aa[:half]+bb[half:]+[cL],GG[half:]+HH[:half]+[Q])
        RP=msm(aa[half:]+bb[:half]+[cR],GG[:half]+HH[half:]+[Q])
        u=RNG.randrange(1,L); ui=inv(u)
        Ls.append(LP); Rs.append(RP); ch.append(u)
        aa=[(aa[i]*u+aa[half+i]*ui)%L for i in range(half)]
        bb=[(bb[i]*ui+bb[half+i]*u)%L for i in range(half)]
        GG=[msm([ui,u],[GG[i],GG[half+i]]) for i in range(half)]
        HH=[msm([u,ui],[HH[i],HH[half+i]]) for i in range(half)]
        nn=half
    s=ipp_verification_scalars(ch); si=[inv(x) for x in s]
    scalars=[aa[0]*x%L for x in s]+[bb[0]*x%L for x in si]+[aa[0]*bb[0]%L]
    points=G+H+[Q]
    for u,LP,RP in zip(ch,Ls,Rs):
        scalars += [-(u*u)%L, -inv(u*u)%L]
        points += [LP,RP]
    reconstructed=msm(scalars,points)
    return reconstructed==P0

def r1cs_trial(n=8):
    aL=[RNG.randrange(L) for _ in range(n)]
    aR=[RNG.randrange(L) for _ in range(n)]
    aO=[aL[i]*aR[i]%L for i in range(n)]
    wL=[RNG.randrange(L) for _ in range(n)]
    wR=[RNG.randrange(L) for _ in range(n)]
    wO=[RNG.randrange(L) for _ in range(n)]
    wc=-(dot(wL,aL)+dot(wR,aR)+dot(wO,aO))%L
    y=RNG.randrange(1,L); yi=inv(y); x=RNG.randrange(1,L)
    ypow=[1]
    for _ in range(1,n): ypow.append(ypow[-1]*y%L)
    yipow=[inv(v) for v in ypow]
    delta=sum((yipow[i]*wR[i]%L)*wL[i]%L for i in range(n))%L
    l1=[(aL[i]+yipow[i]*wR[i])%L for i in range(n)]
    l2=aO[:]
    r0=[(wO[i]-ypow[i])%L for i in range(n)]
    r1=[(ypow[i]*aR[i]+wL[i])%L for i in range(n)]
    t2=(dot(l1,r1)+dot(l2,r0))%L
    expected=(delta-wc)%L
    if t2!=expected: return False
    sL=[RNG.randrange(L) for _ in range(n)]; sR=[RNG.randrange(L) for _ in range(n)]
    l=[(x*l1[i]+x*x*l2[i]+pow(x,3,L)*sL[i])%L for i in range(n)]
    r=[(r0[i]+x*r1[i]+pow(x,3,L)*sR[i])%L for i in range(n)]
    t=dot(l,r)
    t1=dot(l1,r0)
    t3=(dot(l2,r1)+dot(sL,r0))%L
    t4=(dot(l1,sR)+dot(sL,r1))%L
    t5=dot(l2,sR); t6=dot(sL,sR)
    reconstructed=(x*t1+pow(x,2,L)*expected+pow(x,3,L)*t3+pow(x,4,L)*t4+pow(x,5,L)*t5+pow(x,6,L)*t6)%L
    return t==reconstructed

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    ipp={}
    for n in [1,2,4,8,16,32]:
        trials=64 if n<=16 else 32
        passed=sum(ipp_trial(n) for _ in range(trials))
        ipp[str(n)]={'trials':trials,'passed':passed}
        if passed!=trials: raise RuntimeError(f'IPP failed n={n}')
    rtrials=512
    rpassed=sum(r1cs_trial(RNG.choice([1,2,4,8,16])) for _ in range(rtrials))
    if rpassed!=rtrials: raise RuntimeError('R1CS identity failed')
    report={
      'version':1,
      'source_commit':'909fa6ceead557410f756e11a7ce3b3a75a3b222',
      'scalar_modulus':str(L),
      'scope':'Independent scalar-field model of prover/verifier algebra; no Octra C++ arithmetic or group code executed',
      'ipp_reconstruction':ipp,
      'r1cs_polynomial_identity':{'trials':rtrials,'passed':rpassed},
      'checks':{
        'ipp_fold_reconstruction_passed':True,
        'omitted_t2_is_exactly_constraint_term_plus_delta':True,
        'r1cs_t_polynomial_reconstruction_passed':True,
      },
      'security_boundary':[
        'Correct scalar arithmetic is assumed; concrete implementation arithmetic is outside this public algebraic check.',
        'Correct prime-order Ristretto group operations are assumed.',
        'Nonzero Fiat-Shamir challenges are assumed where inversion is required.',
        'No argument-of-knowledge or random-oracle theorem is proved here.',
        'No claim about HFHE confidentiality or syndrome hardness is made.'
      ]
    }
    text=json.dumps(report,indent=2)
    if args.output:
        args.output.write_text(text+'\n', encoding='utf-8')
    print(text)
if __name__=='__main__': main()
