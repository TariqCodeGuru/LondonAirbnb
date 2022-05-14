import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def split_data(df, borough_col, rooms_col, pt_col, split_col, snap_type='mean'):
    '''
    Returns two DataFrames. One above and the other below the selected measure of central tendency for the provided properties.
    df: DataFrame with the Data
    borough_col: The column including the neighbourhood titles
    rooms_col: The column including the number of bedrooms
    pt_col: The column including the property type titles
    split_col: The column including the data to base the split on
    ''' 

    df_above, df_below = pd.DataFrame(), pd.DataFrame()    
    filtered_df = df.loc[:,:]
    
    
    #The lists to iterate through
    property_types = list(df[pt_col].unique())
    boroughs = list(df[borough_col].unique())
    rooms = list(df[rooms_col].unique())

    for b in boroughs:
        for ptype in property_types:
            for room in rooms:
                
                filtered_df = df[(df[borough_col]==b)&(df[pt_col]==ptype)&(df[rooms_col]==room)]
                
                #Generating the premium/discount column for each neighbourhood, property type and bedrooms combo
                #Premium is positive while discount is negative.
                filtered_df.loc[:,'premium_discount'] = filtered_df['price']/filtered_df['price'].mean()-1
                
                #If there is a premium, then true
                filtered_df.loc[:,'premium'] = [bool(x>0) for x in filtered_df['premium_discount']]

                
                #The mean rating for the particular dataset (for a particular neighbourhood, property type and bedroom combination)
                split_point=filtered_df[split_col].mean()
                                
                df_above = pd.concat([df_above, filtered_df[filtered_df[split_col]>split_point]], ignore_index=True)
                df_below = pd.concat([df_below, filtered_df[filtered_df[split_col]<=split_point]], ignore_index=True)
   

    return df_above, df_below


def graph_premium_by(grouped_by_col, above_data, below_data, above_label, below_label, title, xlabel, ylabel):
    '''
    Produces a multiple bar chart with data from the above and below dataframes grouped by the grouped_by_col
    Returns a dataframe with the graphs data.
    grouped_by_col: The column that forms the basis of grouping the data. Also the X-Axis labels.
    above_data: dataframe that is above average
    below_data: dataframe that is below average
    above_label: label to be used in the legend, describing the above average data
    below_label: label to be used in the legend, describing the below average data
    title: the graph's title
    xlabel: the xlabel
    ylabel: the ylabel
    '''
    df = pd.concat([above_data,below_data], ignore_index=True)

    grouped_by_list=list(df[grouped_by_col].unique())
    
    graph_df = pd.DataFrame(columns=[grouped_by_col,'above_premium','above_count','below_premium','below_count'])
    
    for i in grouped_by_list:
        graph_df=graph_df.append({
            grouped_by_col: i,
            'above_premium': above_data[above_data[grouped_by_col]==i]['premium_discount'].mean(),
            'below_premium': below_data[below_data[grouped_by_col]==i]['premium_discount'].mean(),
            'above_count': above_data[above_data[grouped_by_col]==i].shape[0],
            'below_count': below_data[below_data[grouped_by_col]==i].shape[0]
        }, ignore_index=True)

    
    X_axis = np.arange(len(grouped_by_list))

    fontsize=75

    fig, ax = plt.subplots(figsize=(100,50))
    ax.bar(X_axis - 0.2, graph_df['above_premium'], 0.4, label=above_label)
    ax.bar(X_axis + 0.2, graph_df['below_premium'], 0.4, label=below_label)
 
    ax.set_title(title, fontsize=fontsize*2)
    ax.axhline()
    ax.legend(fontsize=fontsize)
    ax.set_xticks(X_axis)
    ax.set_xticklabels(graph_df[grouped_by_col], fontsize=fontsize, rotation=90)
    ax.set_ylabel('Premium/Discount', fontsize=fontsize)

    ax.set_yticklabels(np.around(ax.get_yticks(),2),fontsize=fontsize)

    return graph_df, fig

def compare_premium(grouped_by_col, above_data, below_data, title, xlabel, ylabel, show_graph=False):
    '''
    Produces a bar chart that graphs the above data as percent of the below data.
    Returns a dataframe with the graphs data.
    grouped_by_col: The column that forms the basis of grouping the data. Also the X-Axis labels.
    above_data: dataframe that is above average
    below_data: dataframe that is below average
    above_label: label to be used in the legend, describing the above average data
    below_label: label to be used in the legend, describing the below average data
    title: the graph's title
    xlabel: the xlabel
    ylabel: the ylabel
    '''
    df = pd.concat([above_data,below_data], ignore_index=True)

    grouped_by_list=list(df[grouped_by_col].unique())
    
    graph_df = pd.DataFrame(columns=[grouped_by_col,'premium_discount','count'])
    
    for i in grouped_by_list:
        
        premium_discount=above_data[above_data[grouped_by_col]==i]['price'].mean()\
        /below_data[below_data[grouped_by_col]==i]['price'].mean()-1
        
        count=above_data[above_data[grouped_by_col]==i].shape[0]\
        +below_data[below_data[grouped_by_col]==i].shape[0]
        
        graph_df=graph_df.append({
            grouped_by_col: i,
            'premium_discount': premium_discount,
            'count': count 
        }, ignore_index=True)

    graph_df=graph_df.sort_values('premium_discount')
    if show_graph == True:    
        X_axis = np.arange(len(grouped_by_list))

        fontsize=60
        plt.figure(figsize=(100,50))
        plt.bar(X_axis - 0.2, graph_df['premium_discount'], 0.4)

        plt.xlabel(xlabel, fontsize=fontsize)
        plt.ylabel(ylabel, fontsize=fontsize)
        plt.title(title, fontsize=fontsize*2)

        plt.xticks(X_axis, graph_df[grouped_by_col], rotation=90,fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.show()

    return graph_df

def combine_csv(csv_list,save_csv=False, append_file_name=False):
    '''
    Combines the provided csv files into one DataFrame. The files should have the same columns titles.
    In:
    csv_list: list containing the csv file names to be combined
    save_csv: default=False, indicating that the data will not be saved on a new csv file, if True the data will be saved to a new csv file
    
    Out:
    df: DataFrame containing the combined files
    combined_csv: csv file containing the combined data (saved in the same directory as the python file)
    '''

    df_list=[]
    filename=[]
    
    for f in csv_list:
        df = pd.read_csv(f, parse_dates=True)

        if append_file_name:
            df['filename']=f

        df_list.append(df)

    if save_csv:
        pd.concat(df_list,ignore_index=True).to_csv(f'combined_csv')
        
    return pd.concat(df_list,ignore_index=True)