class CreateHighscores < ActiveRecord::Migration[6.0]
  def change
    create_table :highscores do |t|
      t.string :user
      t.float :time

      t.timestamps
    end
  end
end
