import json
import urllib as url
from xml.dom import minidom
import unicodedata
import time
import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm

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
  print '  Input Query:     ' + artist 

  # 1 - Query the Echonest for this artist
  echo_artist, echo_ID, musicbrainz_ID = query_echonest_artist( artist )

  # 2 - Find this artist in musicbrainz
  discography = query_musicbrainz_artist( musicbrainz_ID )

  # 2a - print discography
  #print_discography( discography )

  # 3 - Retrieve audio features from echonest
  discography = query_echonest_features( echo_artist, echo_ID, discography )

  # 4 - Conduct analysis
  success = sellout_analysis( discography, echo_artist )

# ---------------------
# Echonest artist query
# ---------------------
def query_echonest_artist( artist, DEBUG=False ):

  """

  query_echonest_artist 

  Queries the echonest for an artist user query

  Inputs: artist, string. Input query artist

  Outputs: echo_artist, string    - Echonest artist name
           echo_ID, string        - Echonest ID
           musicbrainz_ID, string - musicbrainz_ID

  """

  # preliminaries
  API_key = 'BI9JKSKATBNC3EYC4' 
  
  base_url = 'http://developer.echonest.com/api/v4/artist/search?api_key=' + API_key

  # build the two query urls
  echo_search_url = base_url + '&name=' + artist + '&format=json&results=1'

  musicbrainz_query = base_url + '&name=' + artist + '&format=json&results=1&bucket=id:musicbrainz'

  # print debug info
  if DEBUG:

    print '  searching for artist in The Echonest...'
  
  # retrieve url
  response = json.loads( url.urlopen( echo_search_url ).read( ) )[ 'response' ]

  # see if successful
  success = response[ 'status' ][ 'message' ] == 'Success'

  # if success
  if success:

    # see if anything returned
    if response[ 'artists' ] != []:

      # get echonest ID
      echo_ID = response[ 'artists' ][ 0 ][ 'id' ]
      
      # and artist name
      echo_name = response[ 'artists' ][ 0 ][ 'name' ]

      # print
      print '  Echonest artist: ' + echo_name

      print '  Echonest ID:     ' + echo_ID 

      # now try and get musicbrainz ID
      musicbrainz_response = json.loads( url.urlopen( musicbrainz_query ).read( ) )[ 'response' ]

      # success?
      musicbrainz_success = response[ 'status' ][ 'message' ] == 'Success'

      if musicbrainz_success:

        # more than 0 results?
        if musicbrainz_response[ 'artists' ][ 0 ][ 'foreign_ids' ] != []:

          # get musicbrainz ID
          musicbrainz_ID = musicbrainz_response[ 'artists' ][ 0 ][ 'foreign_ids' ][ 0 ][ 'foreign_id' ]

          # it's formatted strangely
          musicbrainz_ID = musicbrainz_ID.split('musicbrainz:artist:')[ -1 ]
          
          print '  MusicBrainz ID:  ' + musicbrainz_ID

          return echo_name, echo_ID, musicbrainz_ID

        else:

          # couldn't retrieve the musicbrainz ID
          print_echo_no_musicbrainz()

      else:
      
        # no connection to the echonest
        print_echo_noresponse()

        return None, None, None	

    else:

      # query successful, but no artists returned
      print_echo_no_artist()

      return None, None, None

  # else print error
  else:

    print_echo_noresponse()

    return None, None, None

def print_echo_noresponse( ):

  print '  '
  print '  !!ERROR!!'
  print '  Could not retrieve result from the Echonest'
  print '  '

def print_echo_no_artist( ):

  print '  '
  print '  !!ERROR!!'
  print '  Could not retrieve any matching artists from the Echonest'
  print '  '

def print_echo_no_musicbrainz():

  print '  '
  print '  !!ERROR!!'
  print '  Could not retrieve the musicbrainz ID for this artist'
  print '  '

# ------------------------
# Musicbrainz artist query
# ------------------------
def query_musicbrainz_artist( musicbrainz_ID ):

  """

  query_musicbrainz_artist 

  Queries musicbrainz for an artist user query

  Inputs: musicbrainz_ID, string - Input musicbrainz ID

  Outputs: discography, list -     discography of artist, with each
                                   element being a dictionary of songs,
                                   with the following keys:

                                     'album_name'    - name of album song appears on
                                     'album_date'    - date of album release
                                     'song_title'    - title of song
                                     'track number'  - number it appears on
                                                       album

  """

  # check input
  if musicbrainz_ID == None:

  	return None

  # Preliminaries
  musicbrainz_base_url = 'http://musicbrainz.org/ws/2/release?artist='

  # main storage
  discography = dict()

  # loop through pages 0-75
  for offset in [ '0', '25', '50', '75' ]:

    offset = '0'

    query_url = musicbrainz_base_url + musicbrainz_ID + '&inc=recordings&status=official&type=album&limit=100&offset=' + offset

    #print query_url

    # download xml
    xml = minidom.parse( url.urlopen( query_url ) )

    albums = xml.getElementsByTagName( 'release' )

    for album in albums:

      # must be US release?
      release_country_xml = xml.getElementsByTagName('country')

      release_country = get_country( release_country_xml )

      # Get album title and song list data
      album_title_data = album.getElementsByTagName( 'title' )
  
      # retrieve formatted titles from them
      album_title, song_titles = get_album_title( album_title_data )

      # Get album release date from xml
      release_date_xml = album.getElementsByTagName( 'date' )
 
      # format it
      if release_date_xml == []:

      	continue

      release_year = get_album_release_year( release_date_xml )

      # collect
      album_data = {
                    'album_date': release_year,
                   }

      album_data[ 'tracks' ] = dict()


      for track in song_titles:

        album_data[ 'tracks' ][ track ] = dict()
  	
      # if not seen before, store
      if album_title not in discography:
  	
        discography[ album_title ] = album_data
      
      else:

        # if it precedes the existing data,
        if release_year < discography[ album_title ][ 'album_date' ]:

          # overwrite existing data
          discography[ album_title ] = album_data  	

  return discography

def get_country( country_xml ):

  return country_xml[ 0 ].toprettyxml().strip()[ len( '<country>' ) : -len( '</country>' ) ]

def get_album_title( title_xml ):

  # retrieve title
  album_title = title_xml[ 0 ].toprettyxml().strip()[len('<title>'):-len('</title>')]

  song_titles = [ t.toprettyxml().strip()[ len( '<title>' ) : -len( '</title>' ) ].encode('ascii','ignore').upper() for t in title_xml[ 1: ] ]
  
  return album_title.upper(), song_titles

def get_album_release_year( release_date_xml ):

  date = release_date_xml[ 0 ].toprettyxml().strip()[ len( '<date>' ) : -len( '</date>' ) ]	

  if '-' in date:

  	return int( date.split('-')[ 0 ] )

  else:
  
    return int( date )	

def print_discography( discography ):

  # helper script for getting the right discography

  print ''
  for album, data in discography.items():

    to_print = album + ', ' + str( data[ 'album_date' ] )
    print '  ' + to_print
    print '  ' + '-' * len( to_print )

    for itrack, track in enumerate( data[ 'tracks' ] ):

      print '  ' + str( itrack ) + ': ' + track	
    
    print '  '

# -----------------------
# Echonest audio features
# -----------------------
def query_echonest_features( echo_artist, artist_ID, discography ):

  """

  query_echonest_features

  Queries echonest for a bunch of songs, returning feature 
  vectors

  Inputs: artist_ID, string     - echonest ID for the query artist

           discography, list    - as returned by:

                                    query_musicbrainz_artist( artist )

  Outputs: features, list       - as returned by:

                                    query_echonest_features( artist_ID, discography )

  """

  # empty case
  if artist_ID == None and discography == None:

  	return None

  # preliminaries
  API_key = 'BI9JKSKATBNC3EYC4' 

  song_search_url = 'http://developer.echonest.com/api/v4/song/search?api_key=' + API_key

  song_analyse_url = 'http://developer.echonest.com/api/v4/song/profile?api_key=' + API_key

  # first get all the songs in the echonest API by this artist
  base_tracksearch_url = 'http://developer.echonest.com/api/v4/artist/songs?api_key=' + API_key

  # form track search url
  track_search_url = base_tracksearch_url + '&id=' + artist_ID + '&format=json&start=0&results=99'

  # get response
  echo_tracklist_response = json.loads( url.urlopen( track_search_url ).read( ) )[ 'response' ]

  # format into a dictionary of titles and IDs
  echo_song_IDs = dict()

  for track in echo_tracklist_response[ 'songs' ]:

  	echo_song_IDs[ track[ 'title' ].encode('ascii','ignore').upper() ] = track[ 'id' ] 

  # Main loop
  n_musicbrainz = 0
  n_echo = 0

  print '  Grabbing Echonset summary for songs'
  print '  -----------------------------------'

  for album, data in discography.items():

    for track in data[ 'tracks' ]:

        n_musicbrainz = n_musicbrainz + 1

        if track in echo_song_IDs:

          print '  ' + track

          n_echo = n_echo + 1

          # rate limit
          #time.sleep( 0.5 )

          song_ID = echo_song_IDs[ track ]

          # hence get analysis URL
          analysis_url = song_analyse_url + '&id=' + song_ID + '&bucket=audio_summary'

          # read url
          response = json.loads( url.urlopen( analysis_url ).read( ) )[ 'response' ]

          if response[ 'status' ][ 'message' ] == 'Success':

            if len( response[ 'songs' ] ) > 0:

              audio_summary = response[ 'songs' ][ 0 ][ 'audio_summary' ]

              # store
              for key,attribute in audio_summary.items():

                discography[ album ][ 'tracks' ][ track ][ key ] = attribute

  print ''
  print '  found ' + str( n_echo ) + ' of ' + str( n_musicbrainz ) + ' MusicBrainz songs'
  return discography

# ------------------------
# Conduct sellout analysis
# ------------------------
def sellout_analysis( discography, artist ):

  """

  sellout_analysis

  Conducts 'sellout' analysis on audio features

  Inputs: discography, list        -  discography of artist, with each
                                      element being a dictionary of songs,
                                      with the following keys:

                                        'album_name'    - name of album song appears on
                                        'album_date'    - date of album release
                                        'song_title'    - title of song
                                        'track number'  - number it appears on
                                                          album

  Outputs: sellout_feature, string - which feature in features is indicative
                                     of an artist selling out

              sellout_index, int   - index of selling out index (album)                       
                               
  """

  if discography == None and artist == None:

  	return False
  	
  feature_names = [ 'energy', 'liveness', 'tempo', 'speechiness',
                   'acousticness', 'duration',
                   'loudness', 'valence', 'danceability']

  # are these features global maxes or mins for 
  # 'hardcore' bands?
  feature_max_mins = { 
                       'energy':         'max',
                       'liveness':       'max',
                       'tempo':          'max',
                       'speechiness':    'min',
                       'acousticness':   'min',
                       'duration':       'max',
                       'loudness':       'max',
                       'valence':        'min',
                       'danceability':   'min'
                      }

  # collect median feature values for each album
  for album, songs in discography.items():

    # initialise
    for f in feature_names:

      discography[ album ][ f ] = []

    for song, features in discography[ album ][ 'tracks' ].items():

      if features != {}:

        # and features
        for f in feature_names:

          discography[ album ][ f ].append( features[ f ] )    	
       
  # calculate the medians, standard deviations
  n_features = len( feature_names )

  n_albums = len( discography )

  for ifeat, feature in enumerate( feature_names ):

    vals = []

    album_dates = []

    album_titles = []

    for album, data in discography.items():

      album_dates.append( data[ 'album_date' ] )

      vals.append( np.median( discography[ album ][ feature ] ) )      
  
      album_titles.append( album )

    # sort these vals by album date
    sort_inds = np.argsort( album_dates )

    vals = [ vals[ i ] for i in sort_inds ]

    album_titles = [ album_titles[ i ] for i in sort_inds ]

    album_dates = [ album_dates[ i ] for i in sort_inds ]

    # plot if monotonic max found
    if feature_max_mins[ feature ] == 'max':

      is_sellout, sellout_index = monotonic_max( vals )

    else:

      is_sellout, sellout_index = monotonic_min( vals )
      	
    if is_sellout:

      # plot
      fig, ax = plt.subplots( 1 )

      plt.barh( range( n_albums ),vals, align='center', 
      	              color=cm.PuBu( 0.5 ), edgecolor=cm.PuBu( 0.9 ) )

      fig.patch.set_facecolor('white')

      # Remove all ticks
      ax.xaxis.set_ticks_position('none')
      ax.yaxis.set_ticks_position('none')
      
      # Remove spines
      spines_to_remove = ['top', 'right']

      for spine in spines_to_remove:

        ax.spines[spine].set_visible( False )

      # make lines almost black
      almost_black = '#262626'

      spines_to_keep = ['bottom', 'left']

      for spine in spines_to_keep:

        ax.spines[ spine ].set_linewidth( 0.5 )

        ax.spines[ spine ].set_color( almost_black )

      # tex font
      plt.rc( 'text', usetex=True )
      plt.rc( 'font', family='serif' )
      
      # sort out y limits
      plt.ylim( [ -0.5, n_albums - 0.5 ] )
      
      # xlabel = feature
      plt.xlabel( feature[ 0 ].upper() + feature[ 1 : ] )

      # yticks = album names
      titles_years = [ a[ 0 ] + a[ 1 : ].lower() + ' (' + str( album_dates[ ialbum ] ) + ')' for ialbum,a in enumerate( album_titles ) ]

      plt.yticks( range( len( album_titles ) ), titles_years )

      # title text
      sellout_album = album_titles[ sellout_index ]

      # make a goofy title
      title = 'Scientific$^{*}$ proof that ' + artist + ' sold out after recording ' + sellout_album[ 0 ] + sellout_album[ 1 : ].lower()

      # put a disclaimer
      plt.text( 0, -1, '$^{*}$in no way scientific')

      plt.title( title )

      # tight layout
      plt.tight_layout()

      # save
      plt.savefig( artist + '.pdf')

      return True

  print '  No results found '
  return False

def monotonic_max( feature ):

  max_val = max( feature )

  max_index = np.argmax( feature )

  left_less = all( np.diff( feature[ : max_index + 1 ] ) >= 0 )

  right_less = all( np.diff( feature[ max_index :] ) <= 0 )
  
  mon_max = left_less and right_less

  return mon_max, max_index

def monotonic_min( feature ):

  max_val = min( feature )

  min_index = np.argmin( feature )

  left_more = all( np.diff( feature[ : min_index + 1 ] ) <= 0 )

  right_more = all( np.diff( feature[ min_index :] ) >= 0 )
  
  mon_min = left_more and right_more

  return mon_min, min_index

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
