function createFoldersFromSheet() {
  const ROW_START = 3
  const spreadsheetId = SS_PROVIDERS; 
  const parentFolderId = ID_PROVIDER_ROOT; 

  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(SH_PROVIDERS);
  if (!sheet) {
    Logger.log('Error: No se encontró la hoja con el nombre "proveedores".');
    return;
  }

  const dataRange = sheet.getRange(`A${ROW_START}:A` + sheet.getLastRow());
  const providerNames = dataRange.getValues();

  const parentFolder = DriveApp.getFolderById(parentFolderId);

  providerNames.forEach((row, index) => {
    const providerName = row[0];
    const rowIndex = index + ROW_START; 

    if (providerName) {
      const existingFolders = parentFolder.getFoldersByName(providerName);

      if (existingFolders.hasNext()) {
        folder = existingFolders.next();
        Logger.log(`Folder already exists for: ${providerName}`);
      } else {
        folder = parentFolder.createFolder(providerName);
        Logger.log(`Created folder for: ${providerName}`);
      }
      const folderUrl = folder.getUrl();
      
      const richTextValue = SpreadsheetApp.newRichTextValue()
        .setText('Ver')
        .setLinkUrl(folderUrl)
        .build();
      
      sheet.getRange(rowIndex, 4).setRichTextValue(richTextValue);
    }
  });
}