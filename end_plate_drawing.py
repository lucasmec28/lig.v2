"""Desenho vetorial proporcional, sem imagem gerada por IA."""
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle,Polygon,Arc

BLUE='#176b87';GRAY='#dce4e9';ORANGE='#b36b12';INK='#243844'

def figure(c):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'svg.fonttype':'none'})
    fig,(ax,side)=plt.subplots(1,2,figsize=(10,6.5),gridspec_kw={'width_ratios':[1,1.05]})
    b=c.beam;s=c.support;top=-c.ext_top;bot=b.d+c.ext_bottom
    for a in (ax,side):a.set_aspect('equal');a.axis('off')
    def rect(a,x,y,w,h,fc,ec=INK,lw=1):a.add_patch(Rectangle((x,y),w,h,facecolor=fc,edgecolor=ec,linewidth=lw))
    def dim(a,x1,y1,x2,y2,text,vertical=False):
        a.annotate('',(x1,y1),(x2,y2),arrowprops={'arrowstyle':'<->','color':INK,'lw':.7})
        a.text((x1+x2)/2+(-5 if vertical else 0),(y1+y2)/2+(-6 if not vertical else 0),text,ha='right' if vertical else 'center',va='center',rotation=90 if vertical else 0,fontsize=7,color=INK,bbox={'fc':'white','ec':'none','pad':1})
    rect(ax,-s.bf/2,top-40,s.bf,bot-top+80,'#f3f5f7','#c7cfd5',.6)
    rect(ax,-c.bp/2,top,c.bp,c.hp,'#d2eaf0',BLUE,1.5)
    rect(ax,-b.bf/2,0,b.bf,b.tf,GRAY)
    rect(ax,-b.tw/2,b.tf,b.tw,b.d-2*b.tf,GRAY)
    rect(ax,-b.bf/2,b.d-b.tf,b.bf,b.tf,GRAY)
    for y in c.rows:
        for x in [-c.gauge/2,c.gauge/2]:
            ax.add_patch(Circle((x,y),c.dh/2,facecolor='white',edgecolor=INK,lw=1))
            ax.plot([x-3,x+3],[y,y],color=INK,lw=.6);ax.plot([x,x],[y-3,y+3],color=INK,lw=.6)
    dim(ax,-c.bp/2,top-22,c.bp/2,top-22,f'bp = {c.bp:g}')
    dim(ax,-c.bp/2-30,top,-c.bp/2-30,bot,f'hp = {c.hp:g}',True)
    dim(ax,-c.gauge/2,bot+30,c.gauge/2,bot+30,f'g = {c.gauge:g}')
    if c.kind=='pinned':
        dim(ax,c.bp/2+25,c.rows[0],c.bp/2+25,c.rows[1],f'p = {c.pitch:g}',True)
        ax.text(0,bot+53,f'{len(c.rows)} linhas × 2 parafusos · Ø {c.db:g}',ha='center',fontsize=8)
    else:
        dim(ax,c.bp/2+25,-c.pfo,c.bp/2+25,0,f'pfo = {c.pfo:g}',True)
        dim(ax,c.bp/2+50,b.tf,c.bp/2+50,c.rows[1],f'pfi = {c.pfi:g}',True)
        ax.text(0,bot+53,f'{len(c.rows)} linhas × 2 parafusos · Ø {c.db:g}',ha='center',fontsize=8)
        dim(ax,-c.bp/2-13,top,-c.bp/2-13,c.rows[0],f'e = {c.edge:g}',True)
    ax.set_xlim(-c.bp/2-60,c.bp/2+80);ax.set_ylim(bot+78,top-65)
    ax.set_title('VISTA FRONTAL\nChapa e seção da viga',loc='left',fontsize=10,fontweight='bold',pad=12)
    # Longitudinal slice of column; column depth is deliberately not dimensioned.
    stub=165.;colslice=65.
    rect(side,-s.tf,top-45,s.tf,bot-top+90,GRAY)
    rect(side,-s.tf-colslice,top-45,colslice,bot-top+90,'#f3f5f7','#c7cfd5',.6)
    rect(side,0,top,c.tp,c.hp,'#d2eaf0',BLUE,1.5)
    rect(side,c.tp,0,stub,b.tf,GRAY);rect(side,c.tp,b.d-b.tf,stub,b.tf,GRAY)
    rect(side,c.tp,b.tf,stub,b.d-2*b.tf,'#edf1f4','#bcc8d0',.7)
    for y in c.rows:
        rect(side,-s.tf-10,y-c.db/2,s.tf+c.tp+20,c.db,'#f1e1be',ORANGE,.8)
        rect(side,-s.tf-13,y-c.db*.7,7,c.db*1.4,ORANGE,ORANGE,.8)
        rect(side,c.tp+7,y-c.db*.7,7,c.db*1.4,ORANGE,ORANGE,.8)
    if c.kind=='pinned':
        for y,sign in [(0,-1),(b.d,1)]:side.add_patch(Polygon([(c.tp,y),(c.tp+c.weld,y),(c.tp,y+sign*c.weld)],facecolor=BLUE))
    else:
        for y in [b.tf/2,b.d-b.tf/2]:side.plot([c.tp,c.tp+6],[y-4,y+4],color=BLUE,lw=2)
    dim(side,0,bot+30,c.tp,bot+30,f'tp = {c.tp:g}')
    dim(side,c.tp+stub+23,0,c.tp+stub+23,b.d,f'd = {b.d:g}',True)
    y=b.d/2;side.annotate('N',(c.tp+stub-45,y),(c.tp+stub-90,y),arrowprops={'arrowstyle':'->','color':INK},va='center',fontsize=9)
    side.annotate('V',(c.tp+stub-25,y+70),(c.tp+stub-25,y+15),arrowprops={'arrowstyle':'->','color':INK},ha='center',fontsize=9)
    if c.kind=='moment':
        side.add_patch(Arc((c.tp+70,y),65,65,theta1=80,theta2=290,color=ORANGE,lw=1.3));side.text(c.tp+30,y-45,'M',color=ORANGE,fontsize=10)
    side.set_xlim(-s.tf-colslice-20,c.tp+stub+60);side.set_ylim(bot+78,top-65)
    side.set_title('CORTE LONGITUDINAL\nChapa parafusada à coluna',loc='left',fontsize=9,fontweight='bold',pad=12)
    side.text(-s.tf/2,top-52,'Mesa da coluna',ha='center',fontsize=8)
    side.text(c.tp+stub/2,bot+57,'CJP nas mesas e alma' if c.kind=='moment' else f'Filetes contínuos w = {c.weld:g}',ha='center',fontsize=8,color=BLUE)
    fig.text(.04,.025,'Dimensões em mm · furos padrão · desenho ilustrativo proporcional · coluna mostrada parcialmente',fontsize=8,color=INK)
    fig.subplots_adjust(left=.07,right=.97,top=.88,bottom=.08,wspace=.35)
    return fig

def image_bytes(c,fmt='png'):
    fig=figure(c);out=BytesIO();fig.savefig(out,format=fmt,dpi=190,facecolor='white');plt.close(fig);return out.getvalue()
