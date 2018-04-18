#connect drone to 14550 and there are two upstream streams on 14551 and 14552
FROM lesterthomas/sitlbase:1.1

EXPOSE 14550
EXPOSE 14551
EXPOSE 14552
CMD sleep infinity | python /usr/local/bin/mavproxy.py --out=tcp:0.0.0.0:14550 --out=tcpin:0.0.0.0:14552 --master=tcp:0.0.0.0:14551


