import dictdiffer


def checkBackwardCompatibility(newSchema, jSchemaList):

    for jSchema in jSchemaList:
        differences = list(diff(newSchema, jSchema))

        if differences is None:
            next

        for (operation, listOfDiff, diffAddres) in differences:
            if operation != 'change':
                next

            for elem in listOfDiff:
                if elem == 'type':
                    return False
    return True
