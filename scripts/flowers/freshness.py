"""Assembly freshness from explicit inputs/revisions, never hashes or file sizes."""
def assembly_is_current(job,receipt,pass_number):
 requested=job.get('tiles',[])if pass_number==1 else job.get('rois',[])
 if not requested or any(t['status']not in['accepted','retained']for t in requested):return False
 rows={r['id']:r for r in receipt.get('tiles',[])}
 if set(rows)!={t['id']for t in requested}:return False
 expected=job.get('passProtection',{}).get(str(pass_number))
 if expected is None and not(pass_number==1 and job.get('rois')):expected=job.get('protection')
 if expected is not None and receipt.get('protection')!=expected:return False
 if pass_number==2 and receipt.get('roiRevision',0)!=job.get('roiRevision',0):return False
 for tile in requested:
  row=rows[tile['id']]
  if tile['status']=='retained':
   if row.get('accepted')or row.get('retention')!=tile.get('retention'):return False
  else:
   if not row.get('accepted')or not tile.get('attempts'):return False
   old=row.get('registration',{});new=tile['attempts'][-1]
   if any(old.get(k)!=new.get(k)for k in['candidate','attempt','affineGeneratedToReference']):return False
 return True
