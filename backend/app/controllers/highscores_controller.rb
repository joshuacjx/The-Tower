require 'json'
require 'openssl'

def unpad(text)
  code = text.to_s[-1].ord
  if code <= 16
    return text.delete_suffix(text[-1] * code)
  end
end

class HighscoresController < ApplicationController
  def get_top_ten
    # run code to render the top 10 in json format
    highscores = Highscore.order('time asc').limit(10)    # gets the 10 users with lowest time
    highscorelist = Array.new                             # initialises new array
    highscores.each do |score|                            # iterating through each object in @highscores
      highscorelist.push({                                # appends a new hash object to the new array
        user: score.user,
        time: score.time
      }) 
    end
    jsonlist = highscorelist.to_json                      # convert to json format
    render json: jsonlist                                 # renders the json in the view
  end

  def create_new_highscore
    # posts the new highscore list
    # using AES CBC as the encryption method, with key 'atotallyrandomencryptionkey'
    
    decipher = OpenSSL::Cipher::AES256.new :CBC
    decipher.decrypt
    decipher.padding = 0
    decipher.key = "u8x/A?D(G+KaPdSgVkYp3s6v9y$B&E)H"
    decipher.iv = "LoremIpsumDolorS"

    if request.user_agent == 'The Tower - Game Client'
      userparam = unpad(decipher.update(params[:user]) + decipher.final)
      timeparam = unpad((decipher.update(params[:time]) + decipher.final)).to_f
      highscore = Highscore.new(user: userparam, 
                                time: timeparam)
      if highscore.save
        render status: 201                                # Highscore created
      else
        render status: 500                                # server issue if cannot post
      end
    else
      render status: 401                                  # Unauthorised
    end
  end
end
