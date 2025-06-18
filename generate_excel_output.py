import pandas as pd

def tocsv(contestTitle, patentID, priorArtID, contestLink, filename='output.xlsx'):
    """
    Creates an Excel (.xlsx) spreadsheet from the provided data.

    Args:
        contestTitle (list): List of contest titles.
        patentID (list): List of patent IDs.
        priorArtID (list): List of prior art IDs.
        contestLink (list): List of contest links.
        filename (str, optional): The name of the output Excel file. Defaults to 'output.xlsx'.
    """
    data = {'contestTitle': contestTitle, 'patentID': patentID, 'PriorArtID': priorArtID, 'contestLink': contestLink}
    df = pd.DataFrame(data)

    df.to_excel(filename, index=False)


tocsv([0],[0],[0],[0])
