#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tora_api.traderapi as traderapi
from argparse import Namespace

req_user_login_field = Namespace() 


# 登录用户
UserID = '00032129'
# 登陆密码
Password = '19359120'
# 投资者账户 
InvestorID = '11160150'
# 经济公司部门代码
DepartmentID = '3202'
# 资金账户 
AccountID = '168'
# 沪市股东账号
SSE_ShareHolderID = 'A729598425'
# 深市股东账号
SZSE_ShareHolderID = '0155597516'

req_user_login_field.UserID = UserID
req_user_login_field.Password = Password 
req_user_login_field.UserProductInfo = "HX5ZJ0C1PV"



class TraderSpi(traderapi.CTORATstpTraderSpi):
    def __init__(self, api):
        traderapi.CTORATstpTraderSpi.__init__(self)
        self.__api = api
        self.__req_id = 0
        self.__front_id = 0
        self.__session_id = 0


    def OnFrontConnected(self):
        print('OnFrontConnected')

        # 获取终端信息
        self.__req_id += 1
        #请求登录
        login_req = traderapi.CTORATstpReqUserLoginField()

        # 支持以用户代码、资金账号和股东账号方式登录
		# （1）以用户代码方式登录
        login_req.LogInAccount = UserID
        login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_UserID
		# （2）以资金账号方式登录
        #login_req.DepartmentID = DepartmentID
        #login_req.LogInAccount = AccountID
        #login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_AccountID
		# （3）以上海股东账号方式登录
        #login_req.LogInAccount = SSE_ShareHolderID
        #login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_SHAStock
		# （4）以深圳股东账号方式登录
        #login_req.LogInAccount = SZSE_ShareHolderID
        #login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_SZAStock

		# 支持以密码和指纹(移动设备)方式认证
		# （1）密码认证
		# 密码认证时AuthMode可不填
        #login_req.AuthMode = traderapi.TORA_TSTP_AM_Password
        login_req.Password = Password
		# （2）指纹认证
		# 非密码认证时AuthMode必填
        #login_req.AuthMode = traderapi.TORA_TSTP_AM_FingerPrint
        #login_req.DeviceID = '03873902'
        #login_req.CertSerial = '9FAC09383D3920CAEFF039'
		
	    # 终端信息采集
	    # UserProductInfo填写终端名称
        login_req.UserProductInfo = 'HX5ZJ0C1PV'
	    # 按照监管要求填写终端信息
        login_req.TerminalInfo = 'PC;IIP=123.112.154.118;IPORT=50361;LIP=192.168.118.107;MAC=54EE750B1713FCF8AE5CBD58;HD=TF655AY91GHRVL'
	    # 以下内外网IP地址若不填则柜台系统自动采集，若填写则以终端填值为准报送
        #login_req.MacAddress = '5C-87-9C-96-F3-E3'
        #login_req.InnerIPAddress = '10.0.1.102'
        #login_req.OuterIPAddress = '58.246.43.50'
        ret = self.__api.ReqUserLogin(login_req, self.__req_id)
        if ret != 0:
            print('ReqUserLogin fail, ret[%d]' % ret)
        return ret


    def OnFrontDisconnected(self, nReason: "int") -> "void":
        print('OnFrontDisconnected: [%d]' % nReason)

    
    def OnRspGetConnectionInfo(self, pConnectionInfoField: "CTORATstpConnectionInfoField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int",func: int) -> "void":
        if pRspInfoField.ErrorID == 0:
            print('inner_ip_address[%s]' % pConnectionInfoField.InnerIPAddress)
            print('inner_port[%d]' % pConnectionInfoField.InnerPort)
            print('outer_ip_address[%s]' % pConnectionInfoField.OuterIPAddress)
            print('outer_port[%d]' % pConnectionInfoField.OuterPort)
            print('mac_address[%s]' % pConnectionInfoField.MacAddress)

            #请求登录
            login_req = traderapi.CTORATstpReqUserLoginField()

            # 支持以用户代码、资金账号和股东账号方式登录
		    # （1）以用户代码方式登录
            login_req.LogInAccount = UserID
            login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_UserID
		    # （2）以资金账号方式登录
            #login_req.DepartmentID = DepartmentID
            #login_req.LogInAccount = AccountID
            #login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_AccountID
		    # （3）以上海股东账号方式登录
            #login_req.LogInAccount = SSE_ShareHolderID
            #login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_SHAStock
		    # （4）以深圳股东账号方式登录
            #login_req.LogInAccount = SZSE_ShareHolderID
            #login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_SZAStock

		    # 支持以密码和指纹(移动设备)方式认证
		    # （1）密码认证
		    # 密码认证时AuthMode可不填
            #login_req.AuthMode = traderapi.TORA_TSTP_AM_Password
            login_req.Password = Password
		    # （2）指纹认证
		    # 非密码认证时AuthMode必填
            #login_req.AuthMode = traderapi.TORA_TSTP_AM_FingerPrint
            #login_req.DeviceID = '03873902'
            #login_req.CertSerial = '9FAC09383D3920CAEFF039'
		
		    # 终端信息采集
		    # UserProductInfo填写终端名称
            login_req.UserProductInfo = 'HX5ZJ0C1PV'
		    # 按照监管要求填写终端信息
            login_req.TerminalInfo = 'PC;IIP=123.112.154.118;IPORT=50361;LIP=192.168.118.107;MAC=54EE750B1713FCF8AE5CBD58;HD=TF655AY91GHRVL'
		    # 以下内外网IP地址若不填则柜台系统自动采集，若填写则以终端填值为准报送
            #login_req.MacAddress = '5C-87-9C-96-F3-E3'
            #login_req.InnerIPAddress = '10.0.1.102'
            #login_req.OuterIPAddress = '58.246.43.50'

            self.__req_id += 1
            ret = self.__api.ReqUserLogin(login_req, self.__req_id)
            if ret != 0:
                print('ReqUserLogin fail, ret[%d]' % ret)
            
        else:
            print('GetConnectionInfo fail, [%d] [%d] [%s]!!!' % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspUserLogin(self, pRspUserLoginField: "CTORATstpRspUserLoginField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int",func:int) -> "void":
        if pRspInfoField.ErrorID == 0:
            print('Login success! [%d]' % nRequestID)

            self.__front_id = pRspUserLoginField.FrontID
            self.__session_id = pRspUserLoginField.SessionID

            if func == 1:
                # 查询合约
                req_field = traderapi.CTORATstpQrySecurityField()
                
                #以下字段不填表示不设过滤条件，即查询全部合约
                #req_field.ExchangeID = traderapi.TORA_TSTP_EXD_SSE
                #req_field.SecurityID = '600000'

                #self.__req_id += 1
                ret = self.__api.ReqQrySecurity(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQrySecurity fail, ret[%d]' % ret)
                return

        
        else:
            print('Login fail!!! [%d] [%d] [%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspUserPasswordUpdate(self, pUserPasswordUpdateField: "CTORATstpUserPasswordUpdateField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
        if pRspInfoField.ErrorID == 0:
            print('OnRspUserPasswordUpdate: OK! [%d]' % nRequestID)
        else:
            print('OnRspUserPasswordUpdate: Error! [%d] [%d] [%s]' 
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspOrderInsert(self, pInputOrderField: "CTORATstpInputOrderField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
        if pRspInfoField.ErrorID == 0:
            print('OnRspOrderInsert: OK! [%d]' % nRequestID)
        else:
            print('OnRspOrderInsert: Error! [%d] [%d] [%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspOrderAction(self, pInputOrderActionField: "CTORATstpInputOrderActionField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
        if pRspInfoField.ErrorID == 0:
            print('OnRspOrderAction: OK! [%d]' % nRequestID)
        else:
            print('OnRspOrderAction: Error! [%d] [%d] [%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspInquiryJZFund(self, pRspInquiryJZFundField: "CTORATstpRspInquiryJZFundField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
        if pRspInfoField.ErrorID == 0:
            print('OnRspInquiryJZFund: OK! [%d] [%.2f] [%.2f]'
                % (nRequestID, pRspInquiryJZFundField.UsefulMoney, pRspInquiryJZFundField.FetchLimit))
        else:
            print('OnRspInquiryJZFund: Error! [%d] [%d] [%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspTransferFund(self, pInputTransferFundField: "CTORATstpInputTransferFundField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
        if pRspInfoField.ErrorID == 0:
            print('OnRspTransferFund: OK! [%d]' % nRequestID)
        else:
            print('OnRspTransferFund: Error! [%d] [%d] [%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRtnOrder(self, pOrderField: "CTORATstpOrderField") -> "void":
        print('OnRtnOrder: InvestorID[%s] SecurityID[%s] OrderRef[%d] OrderLocalID[%s] LimitPrice[%.2f] VolumeTotalOriginal[%d] OrderSysID[%s] OrderStatus[%s]'
            % (pOrderField.InvestorID, pOrderField.SecurityID, pOrderField.OrderRef, pOrderField.OrderLocalID, 
            pOrderField.LimitPrice, pOrderField.VolumeTotalOriginal, pOrderField.OrderSysID, pOrderField.OrderStatus))


    def OnRtnTrade(self, pTradeField: "CTORATstpTradeField") -> "void":
        print('OnRtnTrade: TradeID[%s] InvestorID[%s] SecurityID[%s] OrderRef[%d] OrderLocalID[%s] Price[%.2f] Volume[%d]'
            % (pTradeField.TradeID, pTradeField.InvestorID, pTradeField.SecurityID,
               pTradeField.OrderRef, pTradeField.OrderLocalID, pTradeField.Price, pTradeField.Volume))


    def OnRtnMarketStatus(self, pMarketStatusField: "CTORATstpMarketStatusField") -> "void":
        print('OnRtnMarketStatus: MarketID[%s] MarketStatus[%s]'
            % (pMarketStatusField.MarketID, pMarketStatusField.MarketStatus))


    def OnRspQrySecurity(self, pSecurityField: "CTORATstpSecurityField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if bIsLast != 1:
            print('OnRspQrySecurity[%d]: SecurityID[%s] SecurityName[%s] MarketID[%s] OrderUnit[%s] OpenDate[%s] UpperLimitPrice[%.2f] LowerLimitPrice[%.2f]'
                % (nRequestID, pSecurityField.SecurityID, pSecurityField.SecurityName, pSecurityField.MarketID,
                pSecurityField.OrderUnit, pSecurityField.OpenDate, pSecurityField.UpperLimitPrice, pSecurityField.LowerLimitPrice))
        else:
            print('查询合约结束[%d] ErrorID[%d] ErrorMsg[%s]'
            % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspQryInvestor(self, pInvestorField: "CTORATstpInvestorField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if bIsLast != 1:
            print('OnRspQryInvestor[%d]: InvestorID[%s] InvestorName[%s] Operways[%s]'
                %(nRequestID, pInvestorField.InvestorID, pInvestorField.InvestorName, 
                pInvestorField.Operways))
        else:
            print('查询投资者结束[%d] ErrorID[%d] ErrorMsg[%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspQryShareholderAccount(self, pShareholderAccountField: "CTORATstpShareholderAccountField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if bIsLast != 1:
            print('OnRspQryShareholderAccount[%d]: InvestorID[%s] ExchangeID[%s] ShareholderID[%s]'
                %(nRequestID, pShareholderAccountField.InvestorID, pShareholderAccountField.ExchangeID, pShareholderAccountField.ShareholderID))
        else:
            print('查询股东账户结束[%d] ErrorID[%d] ErrorMsg[%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspQryTradingAccount(self, pTradingAccountField: "CTORATstpTradingAccountField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if bIsLast != 1:
            print('OnRspQryTradingAccount[%d]: DepartmentID[%s] InvestorID[%s] AccountID[%s] CurrencyID[%s] UsefulMoney[%.2f] FetchLimit[%.2f]'
                % (nRequestID, pTradingAccountField.DepartmentID, pTradingAccountField.InvestorID, pTradingAccountField.AccountID, pTradingAccountField.CurrencyID,
                pTradingAccountField.UsefulMoney, pTradingAccountField.FetchLimit))
        else:
            print('查询资金账号结束[%d] ErrorID[%d] ErrorMsg[%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))


    def OnRspQryOrder(self, pOrderField: "CTORATstpOrderField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if bIsLast != 1:
            print('OnRspQryOrder[%d]: SecurityID[%s] OrderLocalID[%s] OrderRef[%d] OrderSysID[%s] VolumeTraded[%d] OrderStatus[%s] OrderSubmitStatus[%s], StatusMsg[%s]'
                % (nRequestID, pOrderField.SecurityID, pOrderField.OrderLocalID, pOrderField.OrderRef, pOrderField.OrderSysID, 
                pOrderField.VolumeTraded, pOrderField.OrderStatus, pOrderField.OrderSubmitStatus, pOrderField.StatusMsg))
        else:
            print('查询报单结束[%d] ErrorID[%d] ErrorMsg[%s]'
                 % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))

    def OnRspQryPosition(self, pPositionField: "CTORATstpPositionField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int", bIsLast: "bool") -> "void":
        if bIsLast != 1:
            print('OnRspQryPosition[%d]: InvestorID[%s] SecurityID[%s] HistoryPos[%d] TodayBSPos[%d] TodayPRPos[%d]'
                % (nRequestID, pPositionField.InvestorID, pPositionField.SecurityID, pPositionField.HistoryPos, 
                pPositionField.TodayBSPos, pPositionField.TodayPRPos))
        else:
            print('查询持仓结束[%d] ErrorID[%d] ErrorMsg[%s]'
                 % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))

def main():
    # 打印接口版本号
    print(traderapi.CTORATstpTraderApi_GetApiVersion())

    # 创建接口对象
    # pszFlowPath为私有流和公有流文件存储路径，若订阅私有流和公有流且创建多个接口实例，每个接口实例应配置不同的路径
    # bEncrypt为网络数据是否加密传输，考虑数据安全性，建议以互联网方式接入的终端设置为加密传输
    api = traderapi.CTORATstpTraderApi.CreateTstpTraderApi('./flow', False)

    # 创建回调对象
    spi = TraderSpi(api)

    # 注册回调接口
    api.RegisterSpi(spi)

    # 注册单个交易前置服务地址
    api.RegisterFront('tcp://210.14.72.16:4400') 





    # 注册多个交易前置服务地址，用逗号隔开
    #api.RegisterFront('tcp://10.0.1.101:6500,tcp://10.0.1.101:26500')
    # 注册名字服务器地址，支持多服务地址逗号隔开
    #api.RegisterNameServer('tcp://10.0.1.101:52370')
    #api.RegisterNameServer('tcp://10.0.1.101:52370,tcp://10.0.1.101:62370')

    #订阅私有流
    api.SubscribePrivateTopic(traderapi.TORA_TERT_QUICK)
    #订阅公有流
    api.SubscribePublicTopic(traderapi.TORA_TERT_QUICK)

    # 启动接口
    api.Init()
    spi.OnFrontConnected()
    login_req = traderapi.CTORATstpReqUserLoginField()
    login_req.LogInAccount = UserID
    login_req.LogInAccountType = traderapi.TORA_TSTP_LACT_UserID
    login_req.Password = Password
    login_req.UserProductInfo = 'HX5ZJ0C1PV'
    login_req.TerminalInfo = 'PC;IIP=123.112.154.118;IPORT=50361;LIP=192.168.118.107;MAC=54EE750B1713FCF8AE5CBD58;HD=TF655AY91GHRVL'
    login_req.FrontID = 0 
    login_req.SessionID = 0

    
    rsp_info = traderapi.CTORATstpRspInfoField()
    rsp_info.ErrorID = 0
    rsp_info.FrontID = 0
    rsp_info.SessionID = 0




    spi.OnRspUserLogin(login_req,rsp_info,1,1)

	# 等待程序结束
    input()

    # 释放接口对象
    api.Release()


if __name__ == '__main__':
    main()