def Sellouts( artist ):

  print artist 

  return None

 # name == main biolerplate
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
