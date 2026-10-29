// All demand values are editable concept assumptions, not surveyed resident data.
export const defaults = Object.freeze({units:400,dogShare:25,baths:1,cycle:45,peakShare:60,peakHours:20,availability:90,target:80});
export function capacity(input={}) {
  const p={...defaults,...input};
  for(const [key,value] of Object.entries(p)) if(!Number.isFinite(value)||value<=0) throw new RangeError(`Invalid ${key}`);
  if(p.dogShare>100||p.peakShare>100||p.availability>100||p.target>100) throw new RangeError('Percentages exceed 100');
  const monthly=p.units*p.dogShare/100*p.baths;
  const peakDemand=monthly*p.peakShare/100;
  const hours=4.345*p.peakHours;
  const singleBay=hours*60/p.cycle*p.availability/100;
  const utilization=peakDemand/(singleBay*2)*100;
  const mathematicalBays=Math.max(1,Math.ceil(peakDemand/(singleBay*p.target/100)-1e-10));
  return {monthly,peakDemand,hours,singleBay,utilization,mathematicalBays,recommended:Math.max(2,mathematicalBays)};
}
