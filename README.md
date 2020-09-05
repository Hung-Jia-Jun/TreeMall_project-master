# TreeMall_project

You can download docker image from google drive
[Tree mall docker image download url](https://drive.google.com/file/d/13s_NUqfvCGZAkxhP4mm3jmjC7intnaTE/view?usp=sharing)

# 1. load docker image from local file
docker load --input treemall.tar

# 2. Run Docker image 
docker run -d -p 80:8000 jason/treemall

the service will be automatic running on http://0.0.0.0/index and http://0.0.0.0/shorturl

http://0.0.0.0/index is the order list front-end project
http://0.0.0.0/shorturl is the short url service 
