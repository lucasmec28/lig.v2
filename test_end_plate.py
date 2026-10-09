from dataclasses import replace
from io import BytesIO
import math,json
import pytest
from docx import Document
from lro.end_plate import *
from lro.end_plate_report import create_report

PIN=list(presets().values())[0];MOM=list(presets().values())[2]

def test_dg39_5_3_1_published_yield_line_and_thickness():
    # DG39 printed p.124: bp=8, g=3, h1=26.3, h2=21.7,
    # pfo=2.5, pfi=1.75 (in). Published Yp=186 in; tp=.589 in.
    yp=yield_4e(8,3,26.3,21.7,2.5,1.75)
    assert yp==pytest.approx(186,rel=.002)
    assert thick_required(2640,50,yp)==pytest.approx(.589,abs=.001)
    # Unit invariance is necessary: same thickness in millimetres.
    assert thick_required(2640*4448.221615*25.4,50*6.894757293,yp*25.4)==pytest.approx(.589*25.4,abs=.03)

def test_column_yield_line_independent_substitution():
    b,g,h1,h2,c=250.,100.,434.6,345.8,88.8
    s=math.sqrt(25000)/2
    expected=125*(h1+h2)/s+.02*(h2*(66.6+s)+h1*(22.2+s)+88.8**2/2)+50
    assert yield_column_4e(b,g,h1,h2,c)==pytest.approx(expected)

def test_nbr_current_rigid_plate_and_bolt_interaction():
    # Hand substitution of NBR 6.3.5.3, no prying ignored without a check.
    assert rigid_strip(10000,45,70,400,20)==pytest.approx(math.sqrt(4*35*10000*1.1/(70*400)))
    r=evaluate(replace(PIN,V=60000,N=10000));d={x.id:x for x in r.checks}
    Ab=math.pi*19.05**2/4;ft=.75*830*Ab/1.35;fv=.45*830*Ab/1.35
    assert d['ep_bolt_interaction'].demand==pytest.approx((10000/8/ft)**2+(60000/8/fv)**2)

@pytest.mark.parametrize('c',list(presets().values()))
def test_examples_have_valid_geometry_and_pass_computed_checks(c):
    r=evaluate(c)
    assert not r.issues and r.checks
    assert all(x.passed for x in r.checks)
    assert r.status=='ATENDE ÀS VERIFICAÇÕES REALIZADAS'
    assert EndPlate.from_dict(json.loads(json.dumps(c.to_dict())))==c


def test_minimum_preserves_n_v_direction_but_does_not_amplify_moment():
    c=replace(MOM,N=-1000,V=-11000);r=evaluate(c)
    a=r.geometry['actions']
    assert math.hypot(a['N'],a['V'])==pytest.approx(45000)
    assert a['M']==c.M and a['N']/a['V']==pytest.approx(c.N/c.V)
    assert r.geometry['actual_actions']['V']==c.V


def test_reversed_moment_mirrors_the_symmetric_detail():
    a=evaluate(MOM);b=evaluate(replace(MOM,M=-MOM.M))
    assert [x.ratio for x in a.checks]==pytest.approx([x.ratio for x in b.checks])
    assert evaluate(replace(MOM,layout='top',M=-MOM.M)).status=='GEOMETRIA INVÁLIDA'


def test_more_compression_increases_contact_without_reducing_bolt_tension():
    a=evaluate(replace(MOM,N=-2000,V=50000));b=evaluate(replace(MOM,N=-20000,V=50000))
    assert a.geometry['actions']['bolt_tension']==b.geometry['actions']['bolt_tension']
    assert a.geometry['actions']['C']<b.geometry['actions']['C']

@pytest.mark.parametrize('change',[
    {'kind':'pinned','M':1},{'gauge':50},{'tp':0},{'db':17},{'N':float('nan')},
    {'overhang':2},{'pitch':20},{'bp':70},{'n':True},{'threads':'yes'},
    {'plate_steel':'USI-CIVIL 350'},
])
def test_invalid_pinned_data_never_produces_approval(change):
    r=evaluate(replace(PIN,**change))
    assert r.status=='GEOMETRIA INVÁLIDA' and not r.checks


def test_thin_moment_plate_fails_even_if_some_strength_checks_pass():
    r=evaluate(replace(MOM,tp=12.7,V=45000,M=120000000.))
    assert r.status=='NÃO ATENDE'
    assert not next(x for x in r.checks if x.id=='ep_plate_rigidity').passed


def test_thick_pinned_plate_fails_rotational_detail():
    r=evaluate(replace(PIN,tp=12.7,weld=6))
    # Weld may be valid with the reinforced edge; thickness must not be approved.
    assert r.status!='ATENDE ÀS VERIFICAÇÕES REALIZADAS'


def test_axial_dominance_and_tested_range_are_enforced():
    for c in [replace(MOM,N=300000),replace(MOM,beam=replace(MOM.beam,d=300,clear=260)),replace(MOM,pfo=100)]:
        assert not evaluate(c).checks


def test_no_unbounded_minimum_force_with_small_moment():
    # N may enter the unsupported axial-dominant domain after minimum-force check.
    r=evaluate(replace(MOM,N=1000,V=0,M=1000000))
    assert r.status=='GEOMETRIA INVÁLIDA' and not r.checks


def test_word_order_assumptions_last_and_identity():
    for c in [PIN,MOM]:
        raw=create_report(c,evaluate(c));doc=Document(BytesIO(raw));text='\n'.join(x.text for x in doc.paragraphs)
        assert 'VERIFICAÇÃO INCOMPLETA' not in text
        assert text.index('Premissas adotadas')>text.index('Memória de cálculo')
        assert 'Desenvolvido por LRO Soluções de engenharia LTDA.' in text
        assert doc.element.xpath('.//m:oMath') and doc.inline_shapes
