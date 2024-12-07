import adsk.core, adsk.fusion, traceback
import os


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent
        
        # Get export folder path
        folderDialog = ui.createFolderDialog()
        folderDialog.title = 'Choose Export Folder' 
        if folderDialog.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        exportFolder = folderDialog.folder

        # Get all sketches and select the first one
        sketches = rootComp.sketches
        if sketches.count == 0:
            ui.messageBox('No sketches found in the design')
            return
        
        # Setup export manager
        exportMgr = design.exportManager
        
        # Setup export options
        stlExportOptions = exportMgr.createSTLExportOptions(rootComp)
        stlExportOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
        

        sketch = sketches.item(1)  # Get first sketch


        # Get the diameter
        textResult = ui.inputBox('Enter new diameter (M4, M2, etc):', 'Diameter', '')
        if textResult[0]:
            diameter = textResult[0]
        else:
            return

        # Get the text input from user
        lengthsResult = ui.inputBox('Enter lengths (space seperated):', 'Set Lengths', '')
        if lengthsResult[0]:
            lengths = lengthsResult[0].split(" ")
        else:
            return


        # find the sketch
        texts = sketch.sketchTexts
        if texts.count == 0:
            ui.messageBox('No sketch found with text')
            return  

        oldText = texts.item(0)

        params = design.userParameters
        param = params.itemByName("length")
        if not param:
            ui.messageBox('You need to have a length user param')
            return

        for length in lengths:
            param.expression = str(length)

            oldText.text = f"{diameter} * {length}"
            design.timeline.moveToEnd()

            # Export STL
            name = f"{diameter}.{length}"
            fileName = os.path.join(exportFolder, f'{name}.stl')
            stlExportOptions.filename = fileName
            exportMgr.execute(stlExportOptions)

        # Nut and washer
        param.expression = str(5)
        oldText.text = f"{diameter} * N"
        design.timeline.moveToEnd()
        name = f"{diameter}.nut"
        fileName = os.path.join(exportFolder, f'{name}.stl')
        stlExportOptions.filename = fileName
        exportMgr.execute(stlExportOptions)

        oldText.text = f"{diameter} * W"
        design.timeline.moveToEnd()
        name = f"{diameter}.washer"
        fileName = os.path.join(exportFolder, f'{name}.stl')
        stlExportOptions.filename = fileName
        exportMgr.execute(stlExportOptions)
                
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))