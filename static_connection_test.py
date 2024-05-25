from node_editor.openaiconnection import OpenAIConnection
con = OpenAIConnection()
client1 = con.get_connection()
print(client1)
client2 = con.get_connection()
print(client2)
client3 = con.get_connection()
print(client3)


response = client3.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "system",
      "content": "You will be provided with a message, and your task is to talk about hello world in programming languages."
    },
    {
      "role": "user",
      "content": "How are you?"
    }
  ],
  temperature=0.8,
  max_tokens=64,
  top_p=1
)
print(response.choices[0].message.content)

print(client3)
print(client2)
print(client1)