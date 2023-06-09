import pickle
import pandas as pd
import numpy as np
# contains one ML model and only one recommendation system that we have obtained from the


def predict(user_name):
    '''
    Predicting the top recommended products using best ML models
    '''
    list_data = []
    text_info = ""
    
    # load all input files
    path = "./"
    model_path = path+'Finalized_Model'+".pkl"
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    sent_df = pd.read_pickle(path+"sent_df.pkl")

    ratings_df = pd.read_pickle(path+"ratings_df.pkl")

    mapping = pd.read_pickle(path+"mapping.pkl")

    user_final_rating = pd.read_pickle(path+"user_final_rating.pkl")

    pkl_filename = path+"Tfidf_vectorizer.pkl"
    with open(pkl_filename, 'rb') as file:
        tfidf = pickle.load(file)
    
    if user_name not in user_final_rating.index:
        text_info = "The User "+ user_name +" does not exist. Please provide a valid user name."
    else:
        # Get top 20 recommended products from the best recommendation model
        top20_recommended_products = list(user_final_rating.loc[user_name].sort_values(ascending=False)[0:20].index)
        # Get only the recommended products from the prepared dataframe "df_sent"
        df_top20_products = sent_df[sent_df.id.isin(top20_recommended_products)]
        # For these 20 products, get their user reviews and pass them through TF-IDF vectorizer to convert the data into suitable format for modeling
        X = tfidf.transform(df_top20_products["reviews"].values.astype(str))
        # Use the best sentiment model to predict the sentiment for these user reviews
        df_top20_products['predicted_sentiment'] = model.predict(X)
        # Create a new dataframe "pred_df" to store the count of positive user sentiments
        df_top20_products = df_top20_products[["id","predicted_sentiment"]]
        df_top20_products = pd.merge(mapping,df_top20_products,on="id",how = "inner")
        df_top20_products =  df_top20_products[["name","predicted_sentiment"]]
        pred_df = df_top20_products.groupby(by='name').sum()
        # Create a column to measure the total sentiment count
        pred_df['total_count'] = df_top20_products.groupby(by='name')['predicted_sentiment'].count()
        # Create a column that measures the % of positive user sentiment for each product review
        pred_df['post_percentage'] = np.round(pred_df['predicted_sentiment']/pred_df['total_count']*100,2)
        # Return top 5 recommended products to the user
        result = pred_df.sort_values(by='post_percentage', ascending=False)[:5]
        list_data = list(result.index)
        text_info = "Top 5 Recommended products for \"" + user_name +  "\""
        
    return text_info, list_data