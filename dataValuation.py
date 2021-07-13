import sys
from catchException import exception_handler
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import pandas as pd
import os
# import requests

# import urllib3


## handle exception properly
## make it summarised info , hide traceback
sys.excepthook = exception_handler
#####




def collectApiData(session=None, apitype="surveys", survey_id = 1, limit=40000, offset=0, token=" " ):
    '''
    function takes 6 parameters and returns the data from the api.
    session : request session. this can be reused for the different api type
    apitype:  the type of data to collect. can be answers or surveys. This selection determines the api to be used
    survey_id: each survey has survey id. this is the corresponing survey id . Get the survey id from the surveys api
    limit: the limit of the data to be collected
    offset: the offset where to start next data collection from
    token: the token to be used in the api call

    '''


    ###########################################################################
    #### check if sapi type correct 
    if  apitype == "surveys":
        api = "https://endapi.truefeedback.io/dataplatform/survey/"
    elif apitype == "answers":
        api = 'https://endapi.truefeedback.io/dataplatform/survey/'  + str(survey_id)  + '/'  + 'answers?' + 'limit='+ str(limit) + '&offset=' + str(offset)
    else:
       raise Exception("wrong api type. The api type is a string that can only be answers or surveys")

    ###########################################################################

    ######## inform user of what is happening : that is connection to api is being made ########
    print("The data api endpoint is: ", api)
    ###########################################################################



    ###########################################################################
    ### try catch statement for any error that occurs during connection
    try:
        
        ##
        print("connecting to data api endpoint ...")
        ## configure session retry
        retries = Retry(connect=4,total=3,
                        backoff_factor=0.1,
                        status_forcelist=[ 500, 502, 503, 504 ]) ## force status retry if code returned is 500, 502, 504
    
        ### mount an adapter
        # "pool_maxsize" is the number of connections to keep around per host 
        # (this is useful for multi-threaded applications), whereas "pool_connections" is the number of host-pools
        # to keep around. For example, if you're connecting to 100 different hosts, and pool_connections=10, then only the latest 10 hosts' 
        # connections will be re-used.
        session.mount('http://', HTTPAdapter(max_retries=retries,pool_connections=10, pool_maxsize=10))
        ##

        ### establish a get on the api
        getApi = session.get(api, headers={"auth": token} )
        
        ## the content of the extracted data
        a = getApi.content 
        ## read extracted data into pandas
        df=pd.read_json(a)
        print("my df: ", df.head())
        return df 
    ###########################################################################

    ###########################################################################
    ## from here is the exception statement for try
    #### connection related error
    except  (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError) as e:
        raise Exception('There is an http connection problem. Check the connection configuration', str(e))
    ### value related error
    except ValueError as e:
        raise ValueError('Data not in json format or did you supply wrong token?.', str(e))
    ### catch  keyboard interrupt
    except KeyboardInterrupt as e:
        print(" \t You interrupted the program.")
        try:
            sys.exit(0)
        except:
            os._exit(0)  
    ## if exception not caught from the previous exceptions     
    except:
        raise Exception('a problem has occurred with connection/connection parameters or data format or mising library import or non initialised session')
        #sys.exit()
    ##########################################################################