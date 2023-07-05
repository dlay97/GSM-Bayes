def makeInputGSM(templateName,inputFileName,values):
    '''
    Given a template file name, desired input file name, and a dictionary with specific
    names of characters you wish to replace, replace the names in the template and
    write the new input file.

    An example of how to call this would be:

    # Name of your template file
    template = 'template_5He_3I2-Mao2020.temp'

    # Create a dictionary with the desired key-phrases you've included in your template file
    # note this will only apply to strings with the given name so make it unique!
    testNeut = {"$GSM_NODES":3, "$GSM_CPUS":3, "$L1_d":0.63, "$L1_r0":2.15,
            "$L1_v0":39.5, "$L1_vso":10.7}

    # Name of your desired input file to be created
    inputFile = 'neutron_test.in'

    # call the function to make the input file
    makeInputGSM(template,inputFile,testNeut)
    '''

    # Open our template and read each line into a list
    with open(templateName) as temp:
        fileTemplate = temp.readlines()
    
    # Open our input file as write
    with open(inputFileName,'w') as f:
        # Loop through each input template line
        for line in fileTemplate:
            # loop through each dictionary item name 'key'
            for key, value in values.items():
                # Replace the current dictionary item with its value
                line = line.replace(key, str(value))
            f.write(line)