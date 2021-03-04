

def get_headings(text, master_only=True):
    """
        Returns annotated headings from text in a list form.
        If master_only is set to True, it will return
        only 
    """
    if text == None:
        return NoneType
    else:
        if text.find(","):
            headings = text.split(",")
        else:
            headings = list(text)

        if master_only == False:
            return headings
        else:
            final_headings = list()
            for heading in headings:
                if heading.split("/")[0] not in final_headings:
                    final_headings.append(heading.split("/")[0])
            return final_headings