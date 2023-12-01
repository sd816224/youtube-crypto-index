from flask import Flask, request
from werkzeug.local import LocalProxy   
app = Flask(__name__)

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    request_context=request
    challenge=request_context.args.get('hub.challenge')
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>challenge:',challenge)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>all args:',request_context.args)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>all body:',request_context)
    # if request.method == 'POST':
    # json_response = request.json()
    # data=request['data']
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>header:',challenge)
    if request.method == 'GET':
        return challenge
    # args=json_response['args']
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>data:',data)
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>args:',args)
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>args2:',args2)
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>headers:',json_response['headers'])
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>headers2:',request_context['headers'])
    # # elif request.method=='GET':

    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>request and type:',request, type(request))
    # # request_context=request
    # # param_value=request_context.args.get('hub.challenge')
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>challenge:',param_value)
    

if __name__ == '__main__':
    app.run()



# from werkzeug.local import LocalProxy   
# class asdfs(werkzeug.local.LocalProxy)    
# if request.method == 'POST':
