import base from './playwright.compact-layout.config';
export default {...base,testMatch:'fixed-ux.spec.ts',outputDir:'.tmp-work/fixed-ux/results',projects:[[320,568],[390,844],[768,1024],[1440,900],[844,390]].map(([width,height])=>({name:`${width}x${height}`,use:{viewport:{width,height}}}))};
