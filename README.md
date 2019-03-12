# zabbix_wechat
zabbix  基于wechat的图文报警

报警媒体类型设置：
    * 参数1：{ALERT.SENDTO}
    * 参数2：{ALERT.SUBJECT}
    * 参数3：{ALERT.MESSAGE}
动作设置：
    * 默认标题：
    ```
    故障发生--服务器:{HOSTNAME1}:{TRIGGER.NAME}
    ```
    * 消息内容：
    ```
    主机名:{HOSTNAME1}<br>
    主机IP:{IPADDRESS}<br>
    主机组：{TRIGGER.HOSTGROUP.NAME}<br>
    告警时间:{EVENT.DATE} {EVENT.TIME}<br>
    告警信息: {TRIGGER.NAME}<br>
    告警项目:{TRIGGER.KEY1}<br>
    问题详情:{ITEM.NAME}:{ITEM.VALUE}<br>
    告警值:{TRIGGER.STATUS}:{ITEM.VALUE1}<br>
    事件ID:{EVENT.ID}
    ```
