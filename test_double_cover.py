from dataclasses import replace
from io import BytesIO
import json
import math
from zipfile import ZipFile
import pytest
from lro.double_cover import (DoubleCoverConnection,presets,evaluate,strength,
                              compression_capacity,shim_factor,support_actions,ASSEMBLY_NOTE)
from lro.local_checks import elastic_group
from lro.models import KGF,Profile,STEELS

BASE=next(iter(presets().values()))

def check(c,id):return next(x for x in evaluate(c).checks if x.id==id)

@pytest.mark.parametrize('N,V',[(70000,45000),(-70000,45000),(70000,-45000),(-70000,-45000),(0,11000),(2000,0)])
def test_independent_equilibrium_bolts_and_column(N,V):
    c=replace(BASE,N=N,V=V);a=support_actions(c,V,N)
    # Two level reactions carry the signed axial force and its induced couple.
    assert a['top']+a['bottom']==pytest.approx(N)
    assert (a['top']-a['bottom'])*c.root_height/2==pytest.approx(V*c.pin_x)
    M=V*c.group_e
    f=elastic_group(c.n,c.pitch,1,0,V,N,M)
    y=[(i-(c.n-1)/2)*c.pitch for i in range(c.n)]
    assert sum(fx for fx,fy in f)==pytest.approx(N)
    assert sum(fy for fx,fy in f)==pytest.approx(V)
    assert -sum(yy*fx for yy,(fx,fy) in zip(y,f))==pytest.approx(M)

def test_bolt_hand_calculation_combined_and_two_shear_planes():
    c=replace(BASE,n=2,pitch=70.,edge_v=80.,V=45000.,N=70000.)
    rows,_=strength(c,c.V,c.N,'Conferência manual');a={x.id:x for x in rows}
    # M=45000*(40+5); J=2*35². Critical bolt carries 35000+M/70 horizontally.
    demand=math.hypot(35000+45000*45/70,22500)
    resistance=2*.45*(math.pi*19.05**2/4)*830/1.35
    for side in ('beam','fin'):
        assert a['dc_bolt_'+side].demand==pytest.approx(demand)
        assert a['dc_bolt_'+side].resistance==pytest.approx(resistance)
    assert demand>math.hypot(35000,22500)>max(c.V,c.N)/2

def test_stock_source_is_not_silently_approved():
    c=list(presets().values())[2];r=evaluate(c)
    assert r.status=='GEOMETRIA INVÁLIDA' and not r.checks
    assert any('Passo p' in x.text for x in r.issues)
    assert any('concordâncias' in x.text for x in r.issues)

@pytest.mark.parametrize('N',[2000,-2000])
def test_components_pass_without_full_node_approval(N):
    r=evaluate(replace(BASE,N=N))
    assert len(r.checks)==30 and all(x.passed for x in r.checks)
    assert r.status=='ATENDE ÀS VERIFICAÇÕES REALIZADAS'
    assert any(x.severity=='excluded' and x.text==ASSEMBLY_NOTE for x in r.issues)
    assert all(x.id!='dc_brace' for x in r.checks) # No invented stabilizer-force rule.

def test_minimum_preserves_sign_and_does_not_change_input():
    c=replace(BASE,N=-2000,V=-11000);r=evaluate(c)
    a=r.geometry['actions'];actual=r.geometry['actual_actions']
    assert math.hypot(a['N'],a['V'])==pytest.approx(45000)
    assert a['N']/a['V']==pytest.approx(c.N/c.V)
    assert actual['N']==-2000 and actual['V']==-11000 and c.N==-2000
    for x,y in zip(r.checks,r.actual):assert x.ratio==pytest.approx(y.ratio*r.minimum_factor)

def test_compression_curve_matches_euler_and_is_sensitive_to_length():
    h,t,fy,L,k=200.,8.,250.,180.,2.
    area=h*t;ne=math.pi**2*200000*h*t**3/12/(k*L)**2
    lam=math.sqrt(area*fy/ne);chi=.658**(lam*lam) if lam<=1.5 else .877/(lam*lam)
    rd,p=compression_capacity(h,t,fy,L,k)
    assert rd==pytest.approx(chi*area*fy/1.1)
    assert p['ne']==pytest.approx(ne)
    assert compression_capacity(h,t,fy,2*L,k)[0]<rd
    # No plastic/yield plateau used to sidestep the inconsistent inequality in the supplied scan.
    assert compression_capacity(h,t,fy,1.,1.)[0]<area*fy/1.1

@pytest.mark.parametrize('total,expected',[(0,1),(6.3,1),(10,1-.0154*3.7),(19,1-.0154*12.7)])
def test_filler_factor_boundaries(total,expected):assert shim_factor(total)==pytest.approx(expected)

def test_filler_reduces_bolt_and_bearing_on_affected_side_only():
    c=replace(BASE,fin_t=16.5) # tw=6.5 -> two 5 mm fillers on beam side
    r=evaluate(c);d={x.id:x for x in r.checks};assert len(d)==30
    k=1-.0154*(10-6.3)
    assert d['dc_bolt_beam'].resistance/d['dc_bolt_fin'].resistance==pytest.approx(k)
    lc=min(c.edge_x-c.dh/2,c.edge_v-c.dh/2,c.pitch-c.dh)
    expected=k*min(1.2*lc*c.beam.tw*450,2.4*c.db*c.beam.tw*450)/1.35
    assert d['dc_bearing_beam'].resistance==pytest.approx(expected)
    expected_cover=k*2*min(1.2*lc*c.cover_t*400,2.4*c.db*c.cover_t*400)/1.35
    assert d['dc_bearing_cover'].resistance==pytest.approx(expected_cover)
    assert c.shim_each==5 and c.shim_side=='viga'
    with pytest.raises(ValueError):shim_factor(19.0001)

def test_net_splice_85_percent_limit_and_no_shim_strength_credit():
    c=replace(BASE,n=2,pitch=120,edge_v=50.,db=12.7)
    # Exercise a valid section calculation directly: geometry intentionally separate.
    rows,_=strength(c,0,45000,'Manual');d={x.id:x for x in rows}
    ag=2*c.hp*c.cover_t;an=2*(c.hp-c.n*c.dh_net)*c.cover_t
    ae=min(an,.85*ag);assert ae==pytest.approx(.85*ag)
    assert d['dc_net_cover'].demand==pytest.approx(45000/ae/(400/1.35))
    rows,_=strength(c,0,-45000,'Manual');d={x.id:x for x in rows}
    assert d['dc_net_cover'].demand==0
    assert d['dc_stability_cover'].demand>0

@pytest.mark.parametrize('field,value,phrase',[
    ('gap',0,'Dimensões positivas'),('extension',70,'invade a coluna'),
    ('pitch',20,'Passo p'),('edge_x',5,'Borda horizontal'),
    ('root_height',230,'Distância entre horizontais'),('corner_clip',0,'Alívio de canto'),
    ('weld_web',2,'Filete nervura'),('shim_mode','fit','Diferença de espessuras'),
    ('bolt','ASTM A307','A325 ou A490'),('V',float('nan'),'finitas')])
def test_geometry_and_unsupported_modes_stop_resistance(field,value,phrase):
    r=evaluate(replace(BASE,**{field:value}))
    assert r.status=='GEOMETRIA INVÁLIDA' and not r.checks
    assert any(phrase in x.text for x in r.issues)

def test_zero_and_overload_do_not_receive_approval():
    r=evaluate(replace(BASE,N=0,V=0));assert not r.checks and r.status=='REVISAR CONDIÇÕES DE APLICAÇÃO'
    r=evaluate(replace(BASE,N=-1e6,V=1e6));assert r.status=='NÃO ATENDE'
    assert any(x.text==ASSEMBLY_NOTE for x in r.issues)

def test_project_roundtrip_and_separate_connection_types():
    c=DoubleCoverConnection.from_dict(json.loads(json.dumps(BASE.to_dict())))
    assert c==BASE and c.fixed_assumptions['external_moment_input'] is False
    from lro.examples import presets as old_presets
    old=next(iter(old_presets().values()))
    with pytest.raises(ValueError):DoubleCoverConnection.from_dict(old.to_dict())

def test_report_has_real_equations_pending_and_correct_weld_path():
    from lro.double_cover_report import create_report
    from lxml import etree
    out=create_report(BASE,evaluate(BASE))
    xml=ZipFile(BytesIO(out)).read('word/document.xml')
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
    root=etree.fromstring(xml);text=' '.join(root.xpath('//w:t/text()',namespaces=ns))
    assert ASSEMBLY_NOTE in text and 'ATENDE ÀS VERIFICAÇÕES REALIZADAS' in text
    assert 'as peças centradas' in text and 'As talas são independentes' in text
    assert len(root.xpath('//m:oMath',namespaces=ns))>=12
    assert 'Desenvolvido por LRO Soluções de engenharia LTDA.' in text
    assert 'carini' not in text.lower()

