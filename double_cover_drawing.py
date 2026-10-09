"""Desenho original do detalhe; dimensões reais em mm, sem soldas nas talas."""
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle

INK='#20354a';GRAY='#cbd3da';FIN='#d79749';COVER='#61a5ad';WELD='#b23f36'

def image_bytes(c,fmt='png'):
    with plt.rc_context({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none'}):
        fig,axs=plt.subplots(1,2,figsize=(12,7),gridspec_kw={'width_ratios':[1.2,1]},layout='constrained')
        for ax in axs:ax.set_aspect('equal');ax.axis('off')
        ax,plan=axs;b=c.projection;lf=c.fin_length;xb=lf+c.gap;H=c.root_height;h=c.hp
        rear=-c.support.tw-b;start=lf-2*c.edge_x;end=xb+2*c.edge_x
        far=max(end+70,xb+c.beam.d*.5);vertical=max(c.beam.d/2,H/2+c.stiffener_t)+45
        def rect(a,x,y,w,t,color=GRAY,**kw):
            p=Rectangle((x,y),w,t,facecolor=color,edgecolor=INK,lw=.85,**kw);a.add_patch(p);return p
        def line(a,x,y,**kw):a.plot(x,y,color=kw.pop('color',INK),lw=kw.pop('lw',.8),**kw)
        def dim(a,x1,y1,x2,y2,label):
            a.annotate('',(x2,y2),(x1,y1),arrowprops={'arrowstyle':'<->','lw':.7,'color':INK,'shrinkA':0,'shrinkB':0})
            a.text((x1+x2)/2,(y1+y2)/2,label,ha='center',va='center',rotation=90 if x1==x2 else 0,
                   fontsize=9,color=INK,bbox={'facecolor':'white','edgecolor':'none','pad':1.2})
        def leader(a,label,xy,text):
            a.annotate(label,xy=xy,xytext=text,ha='left',va='center',fontsize=9,color=INK,
                        arrowprops={'arrowstyle':'-','lw':.75,'color':INK})
        ax.set_title('ELEVAÇÃO NA ALMA DA VIGA',loc='left',fontsize=12,fontweight='bold',color=INK,pad=20)
        rect(ax,rear,-vertical,c.support.bf,2*vertical,'#f0f2f4')
        rect(ax,-c.support.tw,-vertical,c.support.tw,2*vertical,'#a3afb9')
        # Quatro horizontais: frente e verso, nos dois níveis.
        for z in (-H/2-c.stiffener_t,H/2):
            rect(ax,0,z,b,c.stiffener_t,GRAY)
            rect(ax,rear,z,b,c.stiffener_t,GRAY)
        outline=[(0,-H/2),(b,-H/2),(b,-h/2),(lf,-h/2),(lf,h/2),(b,h/2),(b,H/2),(0,H/2)]
        ax.add_patch(Polygon(outline,facecolor=FIN,edgecolor=INK,lw=1))
        # Viga afastada da ponta da nervura por g; não encosta na coluna.
        rect(ax,xb,-c.beam.d/2,far-xb,c.beam.d,'#f4f6f7')
        for z in (-c.beam.d/2,c.beam.d/2-c.beam.tf):rect(ax,xb,z,far-xb,c.beam.tf,GRAY)
        rect(ax,start,-h/2,c.cover_length,h,COVER,alpha=.73)
        ys=[(i-(c.n-1)/2)*c.pitch for i in range(c.n)]
        for x in (lf-c.edge_x,xb+c.edge_x):
            for y in ys:ax.add_patch(Circle((x,y),c.dh/2,facecolor='white',edgecolor=INK,lw=1))
        # Apenas interfaces soldadas do conjunto na coluna.
        line(ax,[0,0],[-H/2+c.corner_clip,H/2-c.corner_clip],color=WELD,lw=3)
        for y in (-H/2,H/2):line(ax,[c.corner_clip,b-c.corner_clip],[y,y],color=WELD,lw=3)
        for x in (lf,xb):line(ax,[x,x],[-h/2-25,h/2+30],ls='--',lw=.6)
        dim(ax,b,vertical+18,lf,vertical+18,f'u = {c.extension:g}')
        dim(ax,rear-27,-H/2,rear-27,H/2,f'H = {H:g}')
        dim(ax,far+22,-h/2,far+22,h/2,f'h = {h:g}')
        dim(ax,lf-c.edge_x,-h/2-35,lf,-h/2-35,f'e = {c.edge_x:g}')
        dim(ax,xb,-h/2-35,xb+c.edge_x,-h/2-35,'e')
        leader(ax,f'g = {c.gap:g}',(lf+c.gap/2,h/2+10),(xb+20,h/2+53))
        leader(ax,f'p = {c.pitch:g}',(xb+c.edge_x,(ys[-1]+ys[-2])/2),(far+10,ys[-1]+15))
        leader(ax,'2 talas',(start+12,0),(xb+20,-c.beam.d/2-43))
        ax.text(rear,-vertical-22,'2 níveis × frente/verso = 4 horizontais',fontsize=9,color=INK)
        ax.set_xlim(rear-55,far+75);ax.set_ylim(-vertical-73,vertical+53)

        plan.set_title('PLANTA NO EIXO DA LIGAÇÃO',loc='left',fontsize=12,fontweight='bold',color=INK,pad=20)
        dc=c.support.d;tf=c.support.tf;tn=c.fin_t;tw=c.beam.tw;tt=c.cover_t;tm=max(tn,tw)
        for y in (-dc/2,dc/2-tf):rect(plan,rear,y,c.support.bf,tf,GRAY)
        rect(plan,-c.support.tw,-dc/2+tf,c.support.tw,dc-2*tf,GRAY)
        # Projeção dos horizontais com alívios de canto.
        for x0,x1 in ((0,b),(rear,-c.support.tw)):
            cc=c.corner_clip;yl=-dc/2+tf;yu=dc/2-tf
            pp=[(x0+cc,yl),(x1-cc,yl),(x1,yl+cc),(x1,yu-cc),(x1-cc,yu),(x0+cc,yu),(x0,yu-cc),(x0,yl+cc)]
            plan.add_patch(Polygon(pp,fill=False,edgecolor='#81919f',ls='--',lw=.9))
        rect(plan,0,-tn/2,lf,tn,FIN)
        rect(plan,xb,-tw/2,far-xb,tw,'#a3afb9')
        # Mesas da viga em projeção; sem contato com as talas.
        for y in (-c.beam.bf/2,c.beam.bf/2):line(plan,[xb,far],[y,y],color='#8e9aa5',ls='--')
        for sign in (-1,1):
            y=tm/2 if sign>0 else -tm/2-tt
            rect(plan,start,y,c.cover_length,tt,COVER)
            if c.shim_each>0:
                xx,ww,thin=(start,lf-start,tn) if c.shim_side=='nervura' else (xb,end-xb,tw)
                sy=thin/2 if sign>0 else -tm/2
                rect(plan,xx,sy,ww,c.shim_each,'#ead1ad',hatch='////')
        for x in (lf-c.edge_x,xb+c.edge_x):
            line(plan,[x,x],[-tm/2-tt-6,tm/2+tt+6],lw=2)
            rect(plan,x-c.db*.35,-tm/2-tt-7,c.db*.7,6,'#52687a')
            rect(plan,x-c.db*.4,tm/2+tt+1,c.db*.8,7,'#52687a')
        line(plan,[0,0],[-tn/2-2,tn/2+2],color=WELD,lw=3)
        plan.plot([c.pin_x],[0],marker='+',color=WELD,ms=8,mew=1.5)
        leader(plan,'Nervura soldada',(b/2,tn/2),(10,dc/2+43))
        leader(plan,'Grupo da nervura',(lf-c.edge_x,tm/2+tt+5),(b+17,dc/2-12))
        leader(plan,'Grupo da viga',(xb+c.edge_x,tm/2+tt+5),(xb+20,dc/2-49))
        leader(plan,'Talas só parafusadas',(start+30,-tm/2-tt),(b+20,-dc/2-21))
        leader(plan,'Rótula nominal em g/2',(c.pin_x,0),(b+20,-dc/2-52))
        dim(plan,start,-dc/2-83,end,-dc/2-83,f'L tala = {c.cover_length:g}')
        plan.set_xlim(rear-10,far+88);plan.set_ylim(-dc/2-111,dc/2+71)
        fig.supxlabel(f't nervura = {tn:.3f}   •   t talas = {tt:.3f}   •   t horizontais = {c.stiffener_t:.3f} mm\n'
                      +(f'Calços: 2 × {c.shim_each:.3f} mm no lado da {c.shim_side}.  ' if c.shim_each else 'Contato simétrico conforme ajuste de montagem.  ')
                      +'Vermelho: soldas / referência de rotação. Cotas em mm.',fontsize=10,color=INK)
        out=BytesIO();fig.savefig(out,format=fmt,dpi=170,facecolor='white');plt.close(fig);return out.getvalue()
