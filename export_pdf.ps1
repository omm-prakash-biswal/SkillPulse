$src = 'C:\Users\priya\Downloads\SIH_2026_SYNKRO_SkillPulse_FINAL.pptx'
$dst1 = 'C:\Users\priya\Downloads\SIH_2026_SYNKRO_SkillPulse_FINAL.pdf'
$dst2 = 'C:\Users\priya\OneDrive\Documents\EmployeeTracker\SkillPulse\SIH_2026_SYNKRO_SkillPulse_FINAL.pdf'

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($src, 1, 0, 0)
$pres.SaveAs($dst1, 32)
$pres.SaveAs($dst2, 32)
$pres.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
[GC]::Collect()
[GC]::WaitForPendingFinalizers()
Write-Host "PDF export complete!"
