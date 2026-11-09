# kidi_delivery_app


1. absorption of unrelevant stores if needed .  # Manually 
2. absorption of max cartoons per driver . # Manually
3. absorption of available drivers . # Manually
4. absorption of end-day counting details (boxes,bags) . # Manually
5. allocation division points per driver (each driver start from 1 area). # Auto
6. after the allotment if (driver not reach the max cartoons count,and there is left distribution point. nearest area driver will get the rest of the distribution point unless total of them is higher than the maximum cartoon count per driver it will split for more drivers instead. ). # Auto
7. if there is even more cartoons left after each driver got his max cartoons,
system will suggest possible other drivers who not busy.
8. after all task completed the final step will be to create a file with its details as .docs document & save to specific directory.
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' -MaxEvents 30 | Where-Object {$_.Id -in 3077,3076,3033} | Select-Object TimeCreated, Id, Message | Format-List