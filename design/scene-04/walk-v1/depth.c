/* Orthographic Blender holdout: closest camera-space depth at each pixel centre. */
#include <math.h>
void raster(float *z, int w, int h, const float *tri, int count) {
  for (int i=0; i<count; i++, tri+=9) {
    float x0=tri[0],y0=tri[1],z0=tri[2];
    float ax=tri[3]-x0,ay=tri[4]-y0,az=tri[5]-z0;
    float bx=tri[6]-x0,by=tri[7]-y0,bz=tri[8]-z0,det=ax*by-ay*bx;
    if (fabsf(det)<1.e-6f) continue;
    int l=fmaxf(0,floorf(fminf(x0,fminf(tri[3],tri[6])))),r=fminf(w,ceilf(fmaxf(x0,fmaxf(tri[3],tri[6]))));
    int t=fmaxf(0,floorf(fminf(y0,fminf(tri[4],tri[7])))),b=fminf(h,ceilf(fmaxf(y0,fmaxf(tri[4],tri[7]))));
    for(int y=t;y<b;y++) for(int x=l;x<r;x++) {
      float u=((x+.5f-x0)*by-(y+.5f-y0)*bx)/det,v=(ax*(y+.5f-y0)-ay*(x+.5f-x0))/det;
      if (u>=0 && v>=0 && u+v<=1) {float d=z0+u*az+v*bz; if(d>z[y*w+x]) z[y*w+x]=d;}
    }
  }
}
