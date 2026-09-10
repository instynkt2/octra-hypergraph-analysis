#!/usr/bin/env python3
"""Separate numerical cross-check of the same ideal-model bound.

Uses hypergeometric recurrence for two columns and the elementary inequality
Pr[X <= b] <= z**(-b) E[z**X] (0<z<1) for larger supports, with fixed rational z.
Does not call the published checker's functions. Exact comparisons use Fraction.
This is an AI-assisted second implementation, NOT independent peer review.
"""
from fractions import Fraction as F
from math import comb, log2
from pathlib import Path
import hashlib
import json

m,n,b=8192,16384,258
q=F(385,16384)

def log2fraction(v):
    return log2(v.numerator)-log2(v.denominator)

# Independent calculation using the recurrence of the hypergeometric pmf.
pair=F(0)
pair_details=[]
for a in (192,193):
    for c in (192,193):
        mass=F(comb(m-a,c),comb(m,c))
        tail=F(0)
        for j in range(min(a,c)+1):
            if a+c-2*j<=b:
                tail+=mass
            if j<min(a,c):
                mass*=F((a-j)*(c-j),(j+1)*(m-a-c+j+1))
        pair+=tail/4
        pair_details.append({'a':a,'c':c,'log2_probability':log2fraction(tail)})
pair*=comb(n,2)
if not pair<F(1,2**163): raise ArithmeticError('pair bound failed')

masses=[]
for w in (192,193):
    mass=comb(m,w)*q**w*(1-q)**(m-w)
    if not mass>F(1,36): raise ArithmeticError('domination bound failed')
    masses.append({'weight':w,'mass_approx':float(mass),'density_ratio_approx':float(F(1,2)/mass)})

groups=[(4,4,F(7,80),F(1,2)),(6,16,F(1,8),F(1,2)),
        (18,64,F(1,4),F(1,2)),(66,256,F(7,16),F(1,8))]
covered=[2]
total=pair
rows=[]
for lo,hi,r,z in groups:
    svalues=list(range(lo,hi+1,2))
    covered+=svalues
    # Check every s, not only interval endpoints.
    for s in svalues:
        rs=(1-(1-2*q)**s)/2
        if not rs>r: raise ArithmeticError('r bound failed')
    # For X~Bin(m,rs), z**(-b)*(1-r+rz)**m bounds Pr[X<=b]
    # because rs>r and 0<z<1. Sum the counting factors exactly over the interval.
    bound=z**(-b)*(1-r+r*z)**m*sum(comb(n,s)*18**s for s in svalues)
    if not bound<F(1,2**200): raise ArithmeticError('group bound failed')
    rows.append({'lo':lo,'hi':hi,'r_lower_bound':str(r),'z':str(z),
                 'log2_group_bound_approx':log2fraction(bound),'exact_below_2_minus_200':True})
    total+=bound
if covered!=list(range(2,257,2)): raise ArithmeticError('incomplete support coverage')
if not total<F(1,2**162): raise ArithmeticError('total bound failed')

published=Path(__file__).with_name('sparse_syndrome_checker.py').read_bytes()
git_sha=hashlib.sha1(b'blob '+str(len(published)).encode()+b'\0'+published).hexdigest()
if git_sha!='d748f8d95d0dec42700cd3344e791eb9340f4578': raise ArithmeticError('wrong source version')

out={'scope':'Ideal independent-column model; NOT deployed HFHE security',
     'published_checker_git_blob_sha':git_sha,
     'published_file_identity_verified':True,
     'method':'Exact hypergeometric recurrence and rational exponential-moment bound, separately implemented',
     'all_128_even_support_sizes_covered':True,
     'binomial_masses':masses,
     'individual_pair_tails':pair_details,
     'log2_all_pairs_upper_bound_approx':log2fraction(pair),
     'groups':rows,
     'log2_total_upper_bound_approx':log2fraction(total),
     'exact_total_bound_below_2_minus_162':True,
     'not_independent_peer_review':True}
path=Path(__file__).with_name('independent_recheck_results.json')
path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
