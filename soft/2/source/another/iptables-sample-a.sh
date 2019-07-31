
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
    --dport 22 -j ACCEPT
iptables -A INPUT -i $INTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT
iptables -A INPUT -i $INTERNAL_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 67 -j ACCEPT
iptables -A INPUT -i $INTERNAL_INTERFACE -p icmp -j ACCEPT
iptables -A INPUT -i $DMZ_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 67 -j ACCEPT
iptables -A INPUT -i $DMZ_INTERFACE -p icmp -j ACCEPT
iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT


##############################################################################
##
## OUTPUTチェーンの設定（デフォルト拒否）
##

iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 80 -j ACCEPT
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 443 -j ACCEPT
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p udp -m state --state NEW -m udp \
    --dport 53 -j ACCEPT
iptables -A OUTPUT -o $EXTERNAL_INTERFACE -p icmp -j ACCEPT
iptables -A OUTPUT -o $INTERNAL_INTERFACE -p icmp -j ACCEPT
iptables -A OUTPUT -o $DMZ_INTERFACE -p tcp -m state --state NEW -m tcp \
    --dport 22 -j ACCEPT
iptables -A OUTPUT -m state --state RELATED,ESTABLISHED -j ACCEPT


##############################################################################
##
## FORWARDチェーンの設定（デフォルト拒否）
##

iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 22 -j ACCEPT

iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p udp -m state --state NEW,ESTABLISHED -m udp --dport 53 -j ACCEPT
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 80 -j ACCEPT
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 443 -j ACCEPT
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p icmp -j ACCEPT                                                                                
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $DMZ_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 80 -j ACCEPT
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $DMZ_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 443 -j ACCEPT
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 22 -j ACCEPT
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p udp -m state --state NEW,ESTABLISHED -m udp --dport 53 -j ACCEPT
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 80 -j ACCEPT
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p tcp -m state --state NEW,ESTABLISHED -m tcp --dport 443 -j ACCEPT
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -p icmp -j ACCEPT
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $EXTERNAL_INTERFACE -p icmp -j ACCEPT
iptables -A FORWARD -i $INTERNAL_INTERFACE -o $DMZ_INTERFACE -m state --state NEW,ESTABLISHED -j ACCEPT

iptables -A FORWARD -i $DMZ_INTERFACE -o $INTERNAL_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $DMZ_INTERFACE -o $EXTERNAL_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $DMZ_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $EXTERNAL_INTERFACE -o $INTERNAL_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT
##############################################################################
##
## NATの設定
##

iptables -A POSTROUTING -t nat -s $INTERNAL_LAN -o $EXTERNAL_INTERFACE -j SNAT \
    --to-source $IPADDR

iptables -A POSTROUTING -t nat -s $DMZ_LAN -o $EXTERNAL_INTERFACE -j SNAT \
    --to-source $IPADDR


iptables -A PREROUTING -t nat -p tcp --dport 80 -i $EXTERNAL_INTERFACE -j DNAT --to-destination 192.168.150.2
iptables -A PREROUTING -t nat -p tcp --dport 443 -i $EXTERNAL_INTERFACE -j DNAT --to-destination 192.168.150.2

##############################################################################
##
## 設定の保存
##
#/etc/init.d/iptables save active

## パケットの転送を開始する
echo 1 > /proc/sys/net/ipv4/ip_forward

exit 0