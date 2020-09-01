Rails.application.routes.draw do
  # For details on the DSL available within this file, see https://guides.rubyonrails.org/routing.html
  get '/highscores', to: 'highscores#get_top_ten'
  post '/highscores', to: 'highscores#create_new_highscore'
end
