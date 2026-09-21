const clamp=(n,lo,hi)=>Math.max(lo,Math.min(hi,n));

export function fitMap(view,width,height){
  if(width<=44||height<=44)throw new RangeError('Map needs room for touch targets');
  const points=view.markerBounds?null:view.tracks.flatMap(row=>row.map(t=>t.marker));
  const markerBounds=view.markerBounds??[Math.min(...points.map(p=>p[0])),Math.min(...points.map(p=>p[1])),Math.max(...points.map(p=>p[0])),Math.max(...points.map(p=>p[1]))];
  const groups=[{bounds:view.bounds,pad:8},{bounds:markerBounds,pad:22}];
  // Geometry scales with the map; touch padding stays in CSS pixels.
  let scale=Infinity;
  for(const axis of [0,1])for(const left of groups)for(const right of groups){
    const span=right.bounds[axis+2]-left.bounds[axis];
    if(span>0)scale=Math.min(scale,(([width,height][axis])-left.pad-right.pad)/span);
  }
  const offsets=[width,height].map((size,axis)=>{
    const lo=Math.max(...groups.map(g=>g.pad-g.bounds[axis]*scale));
    const hi=Math.min(...groups.map(g=>size-g.pad-g.bounds[axis+2]*scale));
    return clamp((size-(view.bounds[axis]+view.bounds[axis+2])*scale)/2,lo,hi);
  });
  return {scale,x:offsets[0],y:offsets[1]};
}

export function placeTargets(anchors,width,height){
  const points=anchors.map(p=>p.map((v,k)=>clamp(v,22,[width,height][k]-22)));
  // Rare close passes need a tiny on-roof nudge, not overlapping hit areas.
  for(let pass=0;pass<4;pass++)for(let i=0;i<points.length;i++)for(let j=i+1;j<points.length;j++){
    const delta=points[j].map((p,k)=>p-points[i][k]);
    if(delta.some(d=>Math.abs(d)>=44))continue;
    const axis=Math.abs(delta[0])>Math.abs(delta[1])?0:1;
    const sign=delta[axis]>=0?1:-1,shift=(44.5-Math.abs(delta[axis]))/2;
    points[i][axis]=clamp(points[i][axis]-sign*shift,22,[width,height][axis]-22);
    points[j][axis]=clamp(points[j][axis]+sign*shift,22,[width,height][axis]-22);
  }
  return points;
}
