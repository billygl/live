Sub UnpivotData()
    Dim wsInput As Worksheet
    Dim wsOutput As Worksheet
    Dim LastRow As Long
    Dim i As Long
    Dim j As Long
    Dim rowNum As Long

    ' Set the input and output worksheets
    On Error Resume Next
    Set wsInput = ThisWorkbook.Sheets("data") ' Change "Sheet1" to your actual sheet name
    Set wsOutput = ThisWorkbook.Sheets("dataNew")
    
    ' Clear previous data in the output sheet
    wsOutput.Cells.Clear
    
    ' Get the last column for unpivoting from the user
    Dim colLetter As String
    colLetter = InputBox("Escribe la letra de la última columna (e.g., 'F')." & vbCrLf & _
                         "Esta debe ser la última columna 'Variable'.", "Last Variable Column")
    
    If colLetter = "" Then
        MsgBox "Operation cancelled.", vbInformation
        Exit Sub
    End If

    lastUnpivotCol = wsInput.Columns(colLetter).Column

    ' Add headers to the output sheet
    wsOutput.Range("A1").value = "ID"
    wsOutput.Range("B1").value = "Variable"
    wsOutput.Range("C1").value = "SubVariable"
    wsOutput.Range("D1").value = "Value"

    ' Find the last row of data in the input sheet
    LastRow = wsInput.Cells(wsInput.Rows.Count, "A").End(xlUp).Row + 1

    ' Start writing to the second row of the output sheet
    rowNum = 2

    ' Loop through each row of the input data
    Dim nombres As String
    Dim edad As Variant
    Dim sexo As String
    For i = 2 To LastRow
        Dim ojo As String
        Dim pioNct As Variant
        Dim pioBasal As Variant

        If i Mod 2 = 0 Then
            nombres = wsInput.Cells(i, 1).value
            edad = wsInput.Cells(i, 2).value
            sexo = wsInput.Cells(i, 3).value
            ' Conditionally replace 'M' with '1' and 'F' with '2'
            Dim sexoValue As Variant
            sexoValue = sexo
            If UCase(sexo) = "M" Then
                sexoValue = 1
            ElseIf UCase(sexo) = "F" Then
                sexoValue = 2
            End If
            
            ' ID, Variable, SubVariable, Value
            wsOutput.Cells(rowNum, 1).value = nombres
            wsOutput.Cells(rowNum, 2).value = "Edad"
            wsOutput.Cells(rowNum, 3).value = "-"
            wsOutput.Cells(rowNum, 4).value = edad
            rowNum = rowNum + 1

            wsOutput.Cells(rowNum, 1).value = nombres
            wsOutput.Cells(rowNum, 2).value = "SEXO"
            wsOutput.Cells(rowNum, 3).value = "-"
            wsOutput.Cells(rowNum, 4).value = sexoValue
            rowNum = rowNum + 1
        End If
        ojo = wsInput.Cells(i, 4).value
        
        ' Dynamically process the "variable" columns from column 5 to the last specified column
        For j = 5 To lastUnpivotCol
            ' Get the header and the value for the current column
            Dim variableName As String
            Dim value As Variant

            variableName = wsInput.Cells(1, j).value
            value = wsInput.Cells(i, j).value

            ' Unpivot the data and write to the output sheet
            wsOutput.Cells(rowNum, 1).value = nombres
            wsOutput.Cells(rowNum, 2).value = variableName
            wsOutput.Cells(rowNum, 3).value = ojo
            wsOutput.Cells(rowNum, 4).value = value
            rowNum = rowNum + 1
        Next j
    Next i

    MsgBox "Data unpivoted successfully!", vbInformation
End Sub
