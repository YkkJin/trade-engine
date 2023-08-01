#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import traderapi
''' 注意: 如果提示找不到_tradeapi 且与已发布的库文件不一致时,可自行重命名为_tradeapi.so (windows下为_tradeapi.pyd)'''

#投资者账户 
InvestorID = "00030557";   
'''
该默认账号为共用连通测试使用,自有测试账号请到n-sight.com.cn注册并从个人中心获取交易编码,不是网站登录密码,不是手机号
实盘交易时，取客户号，请注意不是资金账号或咨询技术支持
'''

#操作员账户
UserID = "00030557";	   #同客户号保持一致即可

#资金账户 
AccountID = "00030557";		#以Req(TradingAccount)查询的为准

#登陆密码
Password = "17522830";		#N视界注册模拟账号的交易密码，不是登录密码

DepartmentID = "0001";		#生产环境默认客户号的前4位

SSE_ShareHolderID='A00030557'   #不同账号的股东代码需要接口ReqQryShareholderAccount去查询
SZ_ShareHolderID='700030557'    #不同账号的股东代码需要接口ReqQryShareholderAccount去查询


class TraderSpi(traderapi.CTORATstpTraderSpi):
    def __init__(self, api):
        traderapi.CTORATstpTraderSpi.__init__(self)
        self.__api = api
        self.__req_id = 0
        self.__front_id = 0
        self.__session_id = 0


    def OnFrontConnected(self) -> "void":
        print('OnFrontConnected')

        # 获取终端信息
        self.__req_id += 1
        ret = self.__api.ReqGetConnectionInfo(self.__req_id)
        if ret != 0:
            print('ReqGetConnectionInfo fail, ret[%d]' % ret)


    def OnFrontDisconnected(self, nReason: "int") -> "void":
        print('OnFrontDisconnected: [%d]' % nReason)

    
    def OnRspGetConnectionInfo(self, pConnectionInfoField: "CTORATstpConnectionInfoField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
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
            login_req.UserProductInfo = 'pyapidemo'
		    # 按照监管要求填写终端信息
            login_req.TerminalInfo = 'PC;IIP=000.000.000.000;IPORT=00000;LIP=x.xx.xxx.xxx;MAC=123ABC456DEF;HD=XXXXXXXXXX'
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


    def OnRspUserLogin(self, pRspUserLoginField: "traderapi.CTORATstpRspUserLoginField", pRspInfoField: "CTORATstpRspInfoField", nRequestID: "int") -> "void":
        if pRspInfoField.ErrorID == 0:
            print('Login success! [%d]' % nRequestID)

            self.__front_id = pRspUserLoginField.FrontID
            self.__session_id = pRspUserLoginField.SessionID

            if 0:
                # 修改密码
                req_field = traderapi.CTORATstpUserPasswordUpdateField()
                req_field.UserID = UserID
                req_field.OldPassword = Password
                req_field.NewPassword = '123456'

                self.__req_id += 1
                ret = self.__api.ReqUserPasswordUpdate(req_field, self.__req_id)
                if ret != 0:
                    print('ReqUserPasswordUpdate fail, ret[%d]' % ret)
                return


            if 0:
                # 查询合约
                req_field = traderapi.CTORATstpQrySecurityField()
                
                #以下字段不填表示不设过滤条件，即查询全部合约
                #req_field.ExchangeID = traderapi.TORA_TSTP_EXD_SSE
                #req_field.SecurityID = '600000'

                self.__req_id += 1
                ret = self.__api.ReqQrySecurity(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQrySecurity fail, ret[%d]' % ret)

            if 1:
                # 查询投资者
                req_field = traderapi.CTORATstpQryInvestorField()

                # 以下字段不填表示不设过滤条件
                #req_field.InvestorID = InvestorID

                self.__req_id += 1
                ret = self.__api.ReqQryInvestor(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQryInvestor fail, ret[%d]' % ret)

            if 1:
                # 查询股东账号
                req_field = traderapi.CTORATstpQryShareholderAccountField()

                # 以下字段不填表示不设过滤条件，即查询所有股东账号
                #req_field.ExchangeID = traderapi.TORA_TSTP_EXD_SSE

                self.__req_id += 1
                ret = self.__api.ReqQryShareholderAccount(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQryShareholderAccount fail, ret[%d]' % ret)


            if 0:
                # 查询资金账号
                req_field = traderapi.CTORATstpQryTradingAccountField()

                # 以下字段不填表示不设过滤条件，即查询所有资金账号
                req_field.InvestorID = InvestorID
                req_field.DepartmentID = DepartmentID
                req_field.AccountID = AccountID

                self.__req_id += 1
                ret = self.__api.ReqQryTradingAccount(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQryTradingAccount fail, ret[%d]' % ret)


            if 0:
                # 查询报单
                req_field = traderapi.CTORATstpQryOrderField()

                # 以下字段不填表示不设过滤条件，即查询所有报单
                #req_field.SecurityID = '600000'
                #req_field.InsertTimeStart = '09:35:00'
                #req_field.InsertTimeEnd = '10:00:00'

                # IsCancel字段填1表示只查询可撤报单
                #req_field.IsCancel = 1

                self.__req_id += 1
                ret = self.__api.ReqQryOrder(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQryOrder fail, ret[%d]' % ret)


            if 0:
                # 查询持仓
                req_field = traderapi.CTORATstpQryPositionField()

                # 以下字段不填表示不设过滤条件，即查询所有持仓
                #req_field.SecurityID = '600000'

                self.__req_id += 1
                ret = self.__api.ReqQryPosition(req_field, self.__req_id)
                if ret != 0:
                    print('ReqQryPosition fail, ret[%d]' % ret)


            if 1:
                # 请求报单
                req_field = traderapi.CTORATstpInputOrderField()

                req_field.ExchangeID = traderapi.TORA_TSTP_EXD_SSE
                req_field.ShareholderID = SSE_ShareHolderID
                req_field.SecurityID = '600000'
                req_field.Direction = traderapi.TORA_TSTP_D_Buy
                req_field.VolumeTotalOriginal = 100

                '''
                上交所支持限价指令和最优五档剩撤、最优五档剩转限两种市价指令，对于科创板额外支持本方最优和对手方最优两种市价指令和盘后固定价格申报指令
                深交所支持限价指令和立即成交剩余撤销、全额成交或撤销、本方最优、对手方最优和最优五档剩撤五种市价指令
                限价指令和上交所科创板盘后固定价格申报指令需填写报单价格，其它市价指令无需填写报单价格
                以下以上交所限价指令为例，其它指令参考开发指南相关说明填写OrderPriceType、TimeCondition和VolumeCondition三个字段:
                '''
                req_field.LimitPrice = 7.29
                req_field.OrderPriceType = traderapi.TORA_TSTP_OPT_LimitPrice
                req_field.TimeCondition = traderapi.TORA_TSTP_TC_GFD
                req_field.VolumeCondition = traderapi.TORA_TSTP_VC_AV


                '''
                OrderRef为报单引用，类型为整型，该字段报单时为选填
                若不填写，则系统会为每笔报单自动分配一个报单引用
                若填写，则需保证同一个TCP会话下报单引用严格单调递增，不要求连续递增，至少需从1开始编号
                '''
                #req_field.OrderRef = 1

                '''
                InvestorID为选填，若填写则需保证填写正确
                Operway为委托方式，根据券商要求填写，无特殊说明置空即可
                终端自定义字段，终端可根据需要填写如下字段的值，该字段值不会被柜台系统修改，在报单回报和查询报单时返回给终端
                '''
                #req_field.SInfo = 'sinfo'
                #req_field.IInfo = 123

                '''
                其它字段置空
                '''

                self.__req_id += 1
                ret = self.__api.ReqOrderInsert(req_field, self.__req_id)
                if ret != 0:
                    print('ReqOrderInsert fail, ret[%d]' % ret)

            
            if 0:
                # 请求撤单
                req_field = traderapi.CTORATstpInputOrderActionField()

                req_field.ExchangeID = traderapi.TORA_TSTP_EXD_SSE
                req_field.ActionFlag = traderapi.TORA_TSTP_AF_Delete

    
                # 撤单支持以下两种方式定位原始报单：
                # （1）报单引用方式
                #req_field.FrontID = self.__front_id
                #req_field.SessionID = self.__session_id
                #req_field.OrderRef = 1
                # （2）系统报单编号方式
                req_field.OrderSysID = '110019400000005'


                # OrderActionRef报单操作引用，用法同报单引用，可根据需要选填

                '''
                终端自定义字段，终端可根据需要填写如下字段的值，该字段值不会被柜台系统修改，在查询撤单时返回给终端
                '''
                #req_field.SInfo = 'sinfo'
                #req_field.IInfo = 123

                '''
                委托方式字段根据券商要求填写，无特殊说明置空即可
                其它字段置空
                '''

                self.__req_id += 1
                ret = self.__api.ReqOrderAction(req_field, self.__req_id)
                if ret != 0:
                    print('ReqOrderAction fail, ret[%d]' % ret)


            if 0:
                # 查询集中交易资金
                req_field = traderapi.CTORATstpReqInquiryJZFundField()

                req_field.DepartmentID = DepartmentID
                req_field.AccountID = AccountID
                req_field.CurrencyID = traderapi.TORA_TSTP_CID_CNY

                self.__req_id += 1
                ret = self.__api.ReqInquiryJZFund(req_field, self.__req_id)
                if ret != 0:
                    print('ReqInquiryJZFund fail, ret[%d]' % ret)


            if 0:
                # 资金转移(包括资金调拨和银证转账)
                req_field = traderapi.CTORATstpInputTransferFundField()

                req_field.DepartmentID = DepartmentID
                req_field.AccountID = AccountID
                req_field.CurrencyID = traderapi.TORA_TSTP_CID_CNY
                req_field.Amount = 100000.0

                '''
                转移方向：
                TORA_TSTP_TRNSD_MoveIn表示资金从集中交易柜台调拨至快速交易柜台
                TORA_TSTP_TRNSD_MoveOut表示资金从快速交易柜台调拨至集中交易柜台
                TORA_TSTP_TRNSD_StockToBank表示证券快速交易系统资金转入银行，即出金
                TORA_TSTP_TRNSD_BankToStock表示银行资金转入证券快速交易系统，即入金
                以下说明各场景下字段填值：
                '''
                # （1）资金从集中交易柜台调拨至快速交易柜台
                req_field.TransferDirection = traderapi.TORA_TSTP_TRNSD_MoveIn
                # （2）资金从快速交易柜台调拨至集中交易柜台
                #req_field.TransferDirection = traderapi.TORA_TSTP_TRNSD_MoveOut
                # （3）证券快速交易系统资金转入银行，需填写银行代码和资金密码
                #req_field.TransferDirection = traderapi.TORA_TSTP_TRNSD_StockToBank
                #req_field.BankID = traderapi.TORA_TSTP_BKID_CCB
                #req_field.AccountPassword = '123456'
                # （4）银行资金转入证券快速交易系统，需填写银行代码和银行卡密码
                #req_field.TransferDirection = traderapi.TORA_TSTP_TRNSD_BankToStock
                #req_field.BankID = traderapi.TORA_TSTP_BKID_CCB
                #req_field.BankPassword = '123456'

                '''
                申请流水号ApplySerial字段为选填字段
                若不填写则柜台系统会自动生成一个申请流水号
                若填写则需保证同一个TCP会话下申请流水号不重复
                '''
                #req_field.ApplySerial = 1

                self.__req_id += 1
                ret = self.__api.ReqTransferFund(req_field, self.__req_id)
                if ret != 0:
                    print('ReqTransferFund fail, ret[%d]', ret)

            if 0:
                '''登出,目前登出成功连接会立即被柜台系统断开，终端不会收到OnRspUserLogout应答
                连接断开后接口内部会触发重新连接，为不使连接成功后又触发重新登录，需终端做好逻辑控制
                一般情况下若希望登出，直接调用Release接口即可，释放成功连接将被终端强制关闭，Release接口调用注意事项见下文说明
                '''
                req_field = traderapi.CTORATstpUserLogoutField()

                self.__req_id += 1
                ret = self.__api.ReqUserLogout(req_field, self.__req_id)
                if ret != 0:
                    print('ReqUserLogout fail, ret[%d]' % ret)
        else:
            print('Login fail!!! [%d] [%d] [%s]'
                % (nRequestID, pRspInfoField.ErrorID, pRspInfoField.ErrorMsg))
        return

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
            print('OnRspQryInvestor[%d]: InvestorID[%s]  Operways[%s]'
                %(nRequestID, pInvestorField.InvestorID, 
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

if __name__ == '__main__':
    # 打印接口版本号
    print("TradeAPI Version:::"+traderapi.CTORATstpTraderApi_GetApiVersion())

    # 创建接口对象
    # pszFlowPath为私有流和公有流文件存储路径，若订阅私有流和公有流且创建多个接口实例，每个接口实例应配置不同的路径
    # bEncrypt为网络数据是否加密传输，考虑数据安全性，建议以互联网方式接入的终端设置为加密传输
    api = traderapi.CTORATstpTraderApi.CreateTstpTraderApi('./flow', False)

    # 创建回调对象
    spi = TraderSpi(api)

    # 注册回调接口
    api.RegisterSpi(spi)


    if 1:   #模拟环境，TCP 直连Front方式
        # 注册单个交易前置服务地址
        TD_TCP_FrontAddress="tcp://210.14.72.21:4400" #仿真交易环境
        # TD_TCP_FrontAddress="tcp://210.14.72.15:4400" #24小时环境A套
        # TD_TCP_FrontAddress="tcp://210.14.72.16:9500" #24小时环境B套
        api.RegisterFront(TD_TCP_FrontAddress)
        # 注册多个交易前置服务地址，用逗号隔开 形如: api.RegisterFront("tcp://10.0.1.101:6500,tcp://10.0.1.101:26500")
        print("TD_TCP_FensAddress[sim or 24H]::%s\n"%TD_TCP_FrontAddress)

    else:	#模拟环境，FENS名字服务器方式
        TD_TCP_FensAddress ="tcp://210.14.72.21:42370"; #模拟环境通用fens地址
        '''********************************************************************************
        * 注册 fens 地址前还需注册 fens 用户信息，包括环境编号、节点编号、Fens 用户代码等信息
        * 使用名字服务器的好处是当券商系统部署方式发生调整时外围终端无需做任何前置地址修改
        * *****************************************************************************'''
        fens_user_info_field = traderapi.CTORATstpFensUserInfoField()
        fens_user_info_field.FensEnvID="stock" #必填项，暂时固定为“stock”表示普通现货柜台
        fens_user_info_field.FensNodeID="sim"  #必填项，生产环境需按实际填写,仿真环境为sim
        fens_user_info_field.FensNodeID,="24a" #必填项，生产环境需按实际填写,24小时A套环境为24a
        # fens_user_info_field.FensNodeID="24b" #必填项，生产环境需按实际填写,24小时B套环境为24b
        api.RegisterFensUserInfo(fens_user_info_field)
        api.RegisterNameServer(TD_TCP_FensAddress)
        # 注册名字服务器地址，支持多服务地址逗号隔开 形如:api.RegisterNameServer('tcp://10.0.1.101:52370,tcp://10.0.1.101:62370')
        print("TD_TCP_FensAddress[%s]::%s\n"%(fens_user_info_field.FensNodeID,TD_TCP_FensAddress))

    #订阅私有流
    api.SubscribePrivateTopic(traderapi.TORA_TERT_QUICK)
    #订阅公有流
    api.SubscribePublicTopic(traderapi.TORA_TERT_QUICK)
    '''**********************************
	*	TORA_TERT_RESTART, 从日初开始
	*	TORA_TERT_RESUME, 从断开时候开始
	*	TORA_TERT_QUICK, 从最新时刻开始
	*************************************'''
    # 启动接口
    api.Init()

	# 等待程序结束
    input()

    # 释放接口对象
    api.Release()
