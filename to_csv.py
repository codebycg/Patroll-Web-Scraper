import pandas as pd
def tocsv(contestTitle,patentID,  priorArtID,contestLink):

    data={'contestTitle':contestTitle,'patentID':patentID,'PriorArtID':priorArtID,'contestLink':contestLink}
    df = pd.DataFrame(data)
    
    df.to_csv('output.csv', index=False)

tocsv([0],[0],[0],[0])