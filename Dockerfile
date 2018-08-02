FROM python:2-alpine
RUN apk --no-cache add git
RUN mkdir -p /opt/resource
RUN git clone git://github.com/charlierguo/gmail.git /opt/resource/
COPY gmail_resource/* /opt/resource/
RUN ln -s /opt/resource/in_.py /opt/resource/in
RUN ln -s /opt/resource/out.py /opt/resource/out
RUN ln -s /opt/resource/check.py /opt/resource/check
