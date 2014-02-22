# -----------
# Main method
# -----------
def Sellouts( artist ):

  """

  Sellouts( artist )

  Identifies sellout point of an artist

  Inputs: artist, str. Query artist

  Outputs: None

  """
  
  # spit out query
  print ''
  print '  Input Query: ' + artist 

  # 1 - Query the Echonest for this artist
  echo_artist, echo_ID, musicbrainz_ID = query_echonest_artist( artist )

  # 2 - Find this artist in musicbrainz
  discography = query_musicbrainz_artist( musicbrainz_ID )

  # 3 - Retrieve audio features from echonest
  Features = query_echonest_features( echo_ID, discography )

  # 4 - Conduct analysis
  sellout_feature, sellout_index = sellout_analysis( Features, discography )

  # 5 - Plot graph
  plot_sellouts( Features, discography, 
  	                  sellout_feature, sellout_index )

  return None

# ---------------------
# Echonest artist query
# ---------------------
def query_echonest_artist( artist ):

  """

  query_echonest_artist 

  Queries the echonest for an artist user query

  Inputs: artist, string. Input query artist

  Outputs: echo_artist, string    - Echonest artist name
           echo_ID, string        - Echonest ID
           musicbrainz_ID, string - musicbrainz_ID

  """

  return None, None, None

# ------------------------
# Musicbrainz artist query
# ------------------------
def query_musicbrainz_artist( artist ):

  """

  query_musicbrainz_artist 

  Queries musicbrainz for an artist user query

  Inputs: artist, string. Input musicbrainz ID

  Outputs: discography, list -  discography of artist, with each
                                element being a dictionary of songs,
                                with the following keys:

                                 'album_name'    - name of album song appears on
                                 'album_date'    - date of album release
                                 'song_title'    - title of song
                                 'track number'  - number it appears on
                                                   album

  """

  return None

# -----------------------
# Echonest audio features
# -----------------------
def query_echonest_features( artist_ID, discography ):

  """

  query_echonest_features

  Queries echonest for a bunch of songs, returning feature 
  vectors

  Inputs: artist_ID, string     - echonest ID for the query artist

           discography, list    - as returned by:

                                    query_musicbrainz_artist( artist )

  Outputs: features, list       - list of features, one for every query
                                  ( and in the same order ). Each element is 
                                  either None ( no analysis available ), or a 
                                  dictionary with the following fields, 
                                  (which should be self-explanatory):

                                    'time_signature'
                                    'energy'
                                    'liveness'
                                    'tempo'
                                    'speechiness'
                                    'acousticness'
                                    'mode'
                                    'key'
                                    'duration'
                                    'loudness'
                                    'valance'

  """

  return None

# ------------------------
# Conduct sellout analysis
# ------------------------
def sellout_analysis( features, discography ):

  """

  sellout_analysis

  Conducts 'sellout' analysis on audio features

  Inputs:  features, list          -  list of features, one for every query
                                      ( and in the same order ). Each element is 
                                      either None ( no analysis available ), or a 
                                      dictionary with the following fields, 
                                      (which should be self-explanatory):

                                        'time_signature'
                                        'energy'
                                        'liveness'
                                        'tempo'
                                        'speechiness'
                                        'acousticness'
                                        'mode'                                    
                                        'key'
                                        'duration'
                                        'loudness'
                                        'valance'

           discography, list       -  discography of artist, with each
                                      element being a dictionary of songs,
                                      with the following keys:

                                        'album_name'    - name of album song appears on
                                        'album_date'    - date of album release
                                        'song_title'    - title of song
                                        'track number'  - number it appears on
                                                          album

  Outputs: sellout_feature, string - which feature in features is indicative
                                     of an artist selling out
 
           sellout_type, string    - is the sellout a global maximum ( 'max' )
                                     or minimum ( 'min' )?

              sellout_index, int   - index of selling out index (album)                       
                               
  """

  return None, None

def plot_sellouts( Features, discography, 
	                   sellout_feat, sellout_index ):

  """
 
  plot_sellouts

  Plot a graph showing how an artist has sold out

  Inputs: Features  

  """

  return None

# -----------
# boilerplate
# -----------
if __name__ == '__main__':

  # need sys
  import sys

  # check number of inputs
  arg_in = sys.argv[ 1 : ]

  n_arg_in = len( arg_in )

  if n_arg_in != 1:

    n_arg_in_error = 'You must provide exactly one input argument'

    print '  '
    print '  !!ERROR!!'
    print '  ' + n_arg_in_error
    print '  '

  # else check if a string
  else:

    query_artist = arg_in[ 0 ]

    if type( query_artist ) is not str:

      not_string_error = 'Input must a string'

      print '  '
      print '  !!ERROR!!'
      print '  ' + not_string_error
      print '  '

    else:

      # run query	
      Sellouts( query_artist )	  
