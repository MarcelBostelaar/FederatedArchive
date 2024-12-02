
def getObjectOrNone(model, pk):
    collection = model.objects.filter(pk=pk)
    if collection.count() == 0:
        return None
    return collection.first()

def getObjectOrNoneList(model, pk_list):
    return [getObjectOrNone(model, pk) for pk in pk_list]

def getObjectListOnlySuccesfull(model, pk_list):
    x = [getObjectOrNone(model, pk) for pk in pk_list]
    return [i for i in x if i is not None]