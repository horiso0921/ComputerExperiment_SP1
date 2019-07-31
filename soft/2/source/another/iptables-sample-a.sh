
#!/bin/sh

PATH=/sbin:/bin:/usr/bin:/usr/sbin

## �ϐ��̒�`
EXTERNAL_INTERFACE="enp1s0"       # �O���C���^�t�F�[�X�̖��O
DMZ_INTERFACE="enp2s0"            # DMZ �C���^�t�F�[�X�̖��O
INTERNAL_INTERFACE="enp3s0"       # �����C���^�t�F�[�X�̖��O

# �O���C���^�t�F�[�X��IP�A�h���X
IPADDR=`ip addr show $EXTERNAL_INTERFACE | \
 sed -e 's/^.*inet \([^ \/]*\).*$/\1/p' -e d`
# �����l�b�g���[�N�E�A�h���X
INTERNAL_LAN=`ip addr show $INTERNAL_INTERFACE | \
 sed -e 's/^.*inet \([^ ]*\).*$/\1/p' -e d`

# DMZ�l�b�g���[�N�E�A�h���X
DMZ_LAN=`ip addr show $DMZ_INTERFACE | \
 sed -e 's/^.*inet \([^ ]*\).*$/\1/p' -e d`

ANYWHERE="0.0.0.0/0"

## �ȉ��̐ݒ�����s���Ă���Ԃ̓p�P�b�g�̓]�����~����
echo 0 > /proc/sys/net/ipv4/ip_forward

## ���łɐݒ肳��Ă��郋�[������������
iptables -F
iptables -F -t nat

## �|���V�[�̏����ݒ� -> match���Ȃ��ꍇ�̈���
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

## ���[�v�o�b�N�E�C���^�t�F�[�X�̓��o�͂�������
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

##############################################################################
##
## INPUT�`�F�[���̐ݒ�i�f�t�H���g���ہj
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
## OUTPUT�`�F�[���̐ݒ�i�f�t�H���g���ہj
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
## FORWARD�`�F�[���̐ݒ�i�f�t�H���g���ہj
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
## NAT�̐ݒ�
##

iptables -A POSTROUTING -t nat -s $INTERNAL_LAN -o $EXTERNAL_INTERFACE -j SNAT \
    --to-source $IPADDR

iptables -A POSTROUTING -t nat -s $DMZ_LAN -o $EXTERNAL_INTERFACE -j SNAT \
    --to-source $IPADDR


iptables -A PREROUTING -t nat -p tcp --dport 80 -i $EXTERNAL_INTERFACE -j DNAT --to-destination 192.168.150.2
iptables -A PREROUTING -t nat -p tcp --dport 443 -i $EXTERNAL_INTERFACE -j DNAT --to-destination 192.168.150.2

##############################################################################
##
## �ݒ�̕ۑ�
##
#/etc/init.d/iptables save active

## �p�P�b�g�̓]�����J�n����
echo 1 > /proc/sys/net/ipv4/ip_forward

exit 0