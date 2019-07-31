#!/bin/sh

PATH=/sbin:/bin:/usr/bin:/usr/sbin

## 変数の定義
EXTERNAL_INTERFACE="enp1s0"       # 外側インタフェースの名前
DMZ_INTERFACE="enp2s0"            # DMZ インタフェースの名前
INTERNAL_INTERFACE="enp3s0"       # 内側インタフェースの名前

# 外側インタフェースのIPアドレス
IPADDR=`ip addr show $EXTERNAL_INTERFACE | \
 sed -e 's/^.*inet \([^ \/]*\).*$/\1/p' -e d`
# 内部ネットワーク・アドレス
INTERNAL_LAN=`ip addr show $INTERNAL_INTERFACE | \
 sed -e 's/^.*inet \([^ ]*\).*$/\1/p' -e d`

# DMZネットワーク・アドレス
DMZ_LAN=`ip addr show $DMZ_INTERFACE | \
 sed -e 's/^.*inet \([^ ]*\).*$/\1/p' -e d`

ANYWHERE="0.0.0.0/0"

## 以下の設定を実行している間はパケットの転送を停止する
echo 0 > /proc/sys/net/ipv4/ip_forward

## すでに設定されているルールを消去する
iptables -F
iptables -F -t nat

## ポリシーの初期設定 -> matchしない場合の扱い
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

## ループバック・インタフェースの入出力を許可する
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

##############################################################################
##
## INPUTチェーンの設定（デフォルト拒否）
##

iptables -A INPUT -i $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT # Ext -> Router: SSH

iptables -A INPUT -i $INTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT # Local -> Router: SSH
iptables -A INPUT -i $INTERNAL_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 67 -j ACCEPT # Local -> Router: DHCP server
iptables -A INPUT -i $INTERNAL_INTERFACE -p icmp -j ACCEPT # Local -> Router Ping

iptables -A INPUT -i $DMZ_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 67 -j ACCEPT # DMZ -> Router: DHCP server
iptables -A INPUT -i $DMZ_INTERFACE -p icmp -j ACCEPT # DMZ -> Router: Ping

iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT


##############################################################################
##
## OUTPUTチェーンの設定（デフォルト拒否）
##

iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT # Router -> Ext: SSH
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 80 -j ACCEPT # Router -> Ext: HTTP
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 443 -j ACCEPT # Router -> Ext: HTTPS
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 53 -j ACCEPT # Router -> Ext: DNS
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p icmp -j ACCEPT # Router -> Ext: Ping

iptables -A OUTPUT -o $DMZ_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT # Router -> DMZ: SSH
iptables -A OUTPUT -o $DMZ_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 68 -j ACCEPT # Router -> DMZ: DHCP client

iptables -A OUTPUT -o $INTERNAL_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 68 -j ACCEPT # Router -> Local: DHCP client
iptables -A OUTPUT -o $INTERNAL_INTERFACE -p icmp -j ACCEPT # Router -> Local: Ping

iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT


##############################################################################
##
## FORWARDチェーンの設定（デフォルト拒否）
##

iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $DMZ_INTERFACE -p tcp -m tcp \
    --dport 80 -j ACCEPT # Ext -> DMZ: HTTP
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $DMZ_INTERFACE -p tcp -m tcp \
    --dport 443 -j ACCEPT # Ext -> DMZ: HTTPS
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE \
    -m state --state RELATED,ESTABLISHED -j ACCEPT

iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m tcp \
    --dport 80 -j ACCEPT # DMZ -> Ext: HTTP
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m tcp \
    --dport 443 -j ACCEPT # DMZ -> Ext: HTTPS
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p udp -m udp \
    --dport 53 -j ACCEPT # DMZ -> Ext: DNS
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p icmp \
    -j ACCEPT # DMZ -> Ext: Ping
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $DMZ_INTERFACE \
    -m state --state RELATED,ESTABLISHED -j ACCEPT

iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p tcp \
    -m state --state NEW,ESTABLISHED -m tcp --dport 22 -j ACCEPT # Local -> Ext: SSH
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p tcp \
    -m state --state NEW,ESTABLISHED -m tcp --dport 80 -j ACCEPT # Local -> Ext: HTTP
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p tcp \
    -m state --state NEW,ESTABLISHED -m tcp --dport 443 -j ACCEPT # Local -> Ext: HTTPS
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p udp \
    -m state --state NEW,ESTABLISHED -m udp --dport 53 -j ACCEPT # Local -> Ext: DNS
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p icmp \
    -j ACCEPT # Local -> Ext: Ping
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $INTERNAL_INTERFACE \
    -m state --state RELATED,ESTABLISHED -j ACCEPT

iptables -A FORWARD -i $INTERNAL_INTERFACE -o $DMZ_INTERFACE -j ACCEPT # Local -> DMZ
iptables -A FORWARD -i $DMZ_INTERFACE -o $INTERNAL_INTERFACE \
    -m state --state RELATED,ESTABLISHED -j ACCEPT

##############################################################################
##
## NATの設定
##

iptables -A POSTROUTING -t nat -s $INTERNAL_LAN -o $EXTERNAL_INTERFACE -j SNAT \
    --to-source $IPADDR
iptables -A POSTROUTING -t nat -s $DMZ_LAN -o $EXTERNAL_INTERFACE -j SNAT \
    --to-source $IPADDR

iptables -A PREROUTING -t nat -i $EXTERNAL_INTERFACE -p tcp -m tcp \
    --dport 80 -j DNAT --to-destination 192.168.150.2:80
iptables -A PREROUTING -t nat -i $EXTERNAL_INTERFACE -p tcp -m tcp \
    --dport 443 -j DNAT --to-destination 192.168.150.2:443

##############################################################################
##
## 設定の保存
##
#/etc/init.d/iptables save active

## パケットの転送を開始する
echo 1 > /proc/sys/net/ipv4/ip_forward

exit 0
