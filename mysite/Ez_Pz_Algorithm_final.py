
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from bert_serving.client import BertClient
bc = BertClient(check_length=False)


# In[2]:

print("hello")
S_pos=['Easy to Understand good explanation','Thank you','Please continue making more such videos']
S_neg=['Did not understnad','Totally wrong',' wasted my time']


# In[3]:


csv_file="comments.csv"
df = pd.read_csv(csv_file, encoding = "utf-8")


# In[5]:


comments=df['Comment']


# In[6]:


import pandas as pd


# In[7]:


pd.set_option('display.max_colwidth', -1)


# In[8]:
print("split-----------------")

split_df=df.join(pd.DataFrame(df.Comment.str.split('.', expand=True).stack().reset_index(level=1, drop=True)
                ,columns=['Comment '])).drop('Comment',1).rename(columns=str.strip).reset_index(drop=True)


# In[9]:


split_df=split_df.dropna()


# In[10]:


split_df.dropna(subset=['Comment'], inplace=True)


# In[13]:


cleaned_df=split_df.copy()


# In[14]:


cleaned_df['Comment']=split_df['Comment'].astype(str).str.replace(u'\xa0', '')


# In[15]:


cleaned_df=cleaned_df.drop(cleaned_df[cleaned_df['Comment'].map(len) ==0].index)


# In[16]:


cleaned_df=cleaned_df.drop(cleaned_df[cleaned_df['Comment'].map(len) ==1].index)


# In[17]:


cleaned_df=cleaned_df.drop(cleaned_df[cleaned_df['Comment'].map(len) ==2].index)


# In[19]:


csv_file_2="keyword.csv"
df2 = pd.read_csv(csv_file_2)


# In[20]:


temp=df2.columns.values
df2=pd.DataFrame(df2.values,columns=['Video ID','Title','Views','likes','dislikes'])
df2.loc[len(df2)]=temp


# In[21]:


import spacy
from spacy_langdetect import LanguageDetector
nlp =spacy.load('en_core_web_sm')
nlp.add_pipe(LanguageDetector(), name="language_detector", last=True)

for index, row in cleaned_df.iterrows():
    text=row['Comment']    
    doc = nlp(text)
    try:
        for i, sent in enumerate(doc.sents):
    #         print(i)
    #         print(sent)
    #         print(text)
            if (sent._.language['language']!='en'):
                cleaned_df.drop(index, inplace=True)
    #             print(text)
    #             print(index)
    #             print(sent._.language['language'])
    #             print("-------------------------------------------")
    except:
        pass
            
        


# In[22]:


df2['likes']=df2['likes'].astype(int)
df2['dislikes']=df2['dislikes'].astype(float)
df2['Views']=df2['Views'].astype(float)

# In[23]:


df2 = df2[df2.likes > -1]
cleaned_df_new=cleaned_df.merge(df2,on=['Video ID','Title'],how='inner')


# In[26]:


cleaned_df_new_2000=cleaned_df_new


# In[27]:


comments=cleaned_df_new_2000['Comment']
comments=comments.dropna(how='all')
list_comments=list(comments)


# In[28]:


encoding_top=bc.encode(list_comments)


# In[29]:


S_pos=['I like this tutorial','Easy to Understand good explanation','Thank you very much for this It was great','Please continue making more such videos','more than amazing','to the point','you are great']
S_neg=['Did not understnad','Totally wrong',' wasted my time','I am confused','useless. height of uslessness','please remove your video','not possible']


# In[30]:


S_pos_enc=bc.encode(S_pos)
S_neg_enc=bc.encode(S_neg)


# In[31]:


cleaned_df_new_2000['cluster']=99


# In[32]:


s1=0
s2=0
c1=[]
c2=[]
val1=[]
val2=[]
temp=0
for i in encoding_top:
    s1=0
    s2=0
    for x in S_pos_enc:
        s1=s1+np.linalg.norm(i-x)
        
    for y in S_neg_enc:
        s2=s2+np.linalg.norm(i-y)
    
    
    if(s1>s2):
        c1.append(i)
        val1.append(list_comments[temp])
        cleaned_df_new_2000['cluster'].iloc[temp]=1
    else:
        c2.append(i)
        val2.append(list_comments[temp])
        cleaned_df_new_2000['cluster'].iloc[temp]=2
    temp=temp+1


# In[35]:




cleaned_df_new_2000['likes_dislikes_calc']=(cleaned_df_new_2000['likes']-cleaned_df_new_2000['dislikes'])/cleaned_df_new_2000['Views']


# In[36]:


statistics=cleaned_df_new_2000.groupby(['Video ID','Title','cluster'])['cluster'].size().unstack().reset_index()


# In[39]:


statistics['pos_neg_comm']=999
statistics['pos_neg_comm']=(statistics[2]-statistics[1])/(statistics[2]+statistics[1])


# In[40]:


statistics_new=statistics.merge(cleaned_df_new_2000,on=['Video ID','Title'],how='inner')


# In[42]:


statistics_new['score']=9999
statistics_new['score']=(statistics_new['pos_neg_comm']+statistics_new['likes_dislikes_calc'])*1000000


# In[43]:


final=statistics_new.drop_duplicates(subset='Video ID', keep="last")


# In[52]:


final=final.sort_values(by=['score'],ascending=False)


# In[53]:


final['url']='0'
final['url']='https://www.youtube.com/watch?v='+final['Video ID']


# In[55]:


final_list=list(final['url'])
print(final_list)

f= open("output.txt","w")
for i in final_list:
    f.write(i)
    f.write("\n")