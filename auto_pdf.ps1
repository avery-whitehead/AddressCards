$outputFolder = 'C:\Users\jwhitehead\Documents\Python\Address Postcards\out'
# Gets a list of unique UPRNs based on the filenames in the output folder
$uprns = Get-ChildItem $outputFolder | Where { $_.Extension -eq '.html' -and $_.Name  -NotLike 'template*' } | ForEach-Object { $_.Name.Substring(0, 12) } | Get-Unique

foreach ($uprn in $uprns) {
    $addrParam = "$outputFolder\$uprn-addr.html"
    $calParam = "$outputFolder\$uprn-cal.html"
    $output = "$uprn.pdf"
    Invoke-Expression "& .\wkhtmltopdf.exe --margin-top 0 --margin-bottom 0 --margin-left 0 --margin-right 0 --disable-smart-shrinking --page-width '2480px' --page-height '1754px' `"$addrParam`" `"$calParam`" $output"
}
