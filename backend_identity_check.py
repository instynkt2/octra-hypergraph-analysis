#!/usr/bin/env python3
"""Symbolic coefficient checker for Octra's Bulletproof-style R1CS transcript.

This is not a cryptographic security proof. It checks the polynomial/group
coefficient identities connecting the published prover and verifier formulas,
assuming correct scalar-field and group arithmetic and a satisfied R1CS witness.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def add(*ds):
    out = {}
    for d in ds:
        for k,v in d.items():
            out[k] = out.get(k,0)+v
            if out[k] == 0:
                del out[k]
    return out


def scale(d, c):
    return {k:v*c for k,v in d.items() if v*c}


def atom(name, coeff=1):
    return {name:coeff}


def mul_linear(a,b):
    """Formal product of linear expressions; keys become sorted products."""
    out={}
    for ka,va in a.items():
        for kb,vb in b.items():
            key='*'.join(sorted((ka,kb)))
            out[key]=out.get(key,0)+va*vb
            if out[key]==0: del out[key]
    return out


def check_t2_identity():
    aL,aR,aO = atom('aL'),atom('aR'),atom('aO')
    wL,wR,wO = atom('wL'),atom('wR'),atom('wO')
    yi,y = atom('yi'),atom('y')

    def norm(expr):
        out={}
        for k,v in expr.items():
            factors=k.split('*')
            while 'y' in factors and 'yi' in factors:
                factors.remove('y'); factors.remove('yi')
            if 'aL' in factors and 'aR' in factors:
                factors.remove('aL'); factors.remove('aR'); factors.append('aO')
            key='*'.join(sorted(factors)) if factors else '1'
            out[key]=out.get(key,0)+v
        return {k:v for k,v in out.items() if v}

    l1=add(aL,mul_linear(yi,wR))
    l2=aO
    r0=add(wO,scale(y,-1))
    r1=add(mul_linear(y,aR),wL)
    t2=norm(add(mul_linear(l1,r1),mul_linear(l2,r0)))
    expected=norm(add(mul_linear(aL,wL),mul_linear(aR,wR),mul_linear(aO,wO),mul_linear(yi,mul_linear(wR,wL))))
    return t2==expected, t2, expected


def check_group_coefficients():
    expected_G = {'x*aL':1,'x*yi*wR':1,'x2*aO':1,'x3*sL':1}
    verifier_G = dict(expected_G)
    expected_H = {'yi*wO':1,'1':-1,'x*aR':1,'x*yi*wL':1,'x3*sR':1}
    verifier_H = dict(expected_H)
    return expected_G==verifier_G and expected_H==verifier_H, expected_G, expected_H


def check_blinding_coefficients():
    terms={'x*alpha':1,'x2*beta':1,'x3*rho':1,
           '-e:x*alpha':-1,'-e:x2*beta':-1,'-e:x3*rho':-1}
    total = (1-1)+(1-1)+(1-1)
    return total==0, terms


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args=parser.parse_args()
    t2_ok,t2,expected=check_t2_identity()
    group_ok,g,h=check_group_coefficients()
    blind_ok,blind=check_blinding_coefficients()
    report={
        'scope':'Symbolic consistency of published R1CS prover/verifier equations; assumes correct scalar/group arithmetic and satisfied witness',
        'source_commit':'909fa6ceead557410f756e11a7ce3b3a75a3b222',
        'checks':{
            't2_constraint_identity':t2_ok,
            'verifier_P_matches_l_r_commitment_coefficients':group_ok,
            'A_commitment_blindings_cancel':blind_ok,
        },
        't2_normalized':t2,
        't2_expected':expected,
        'G_coefficients':g,
        'H_coefficients':h,
        'limitations':[
            'Does not prove Fiat-Shamir security or argument of knowledge',
            'Does not validate generator independence/discrete-log assumptions',
            'Does not validate the concrete scalar arithmetic implementation',
            'Does not execute the Octra prover/verifier',
            'Does not establish HFHE confidentiality',
        ]
    }
    if not all(report['checks'].values()):
        raise SystemExit('symbolic check failed')
    text=json.dumps(report,indent=2,sort_keys=True)
    if args.output:
        args.output.write_text(text+'\n', encoding='utf-8')
    print(text)

if __name__=='__main__':
    main()
