FROM router:base

COPY Router/route.sh /root/route.sh
COPY Router/multicast_proxy.py /root/multicast_proxy.py

RUN chmod +x /root/route.sh

ENTRYPOINT /root/route.sh
