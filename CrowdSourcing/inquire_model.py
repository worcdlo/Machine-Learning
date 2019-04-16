class INQUIRE():
    def  __init__(self, wkr_update_thres = 7):
        self.wkr_update_thres = wkr_update_thres

        
    class WorkerModel():
        def  __init__(self, wkr_ID):
            self.ID = wkr_ID
            self.confusion_matrix = [[0.3, 0.2], [0.2, 0.3]]
            self.gamma = 0.6
            self.confidence_array = [0.5, 0.5]
            self.confidence = 0.5

            
    class QuestionModel():
        def  __init__(self, qstn_ID, contributor = None, true_prob = 0.5):
            self.ID = qstn_ID
            self.contributor = contributor
            self.true_prob = true_prob
            self.ans_lt = []
            self.qstn_result = -1

            
    def update_qstn_model(self, qstn_model, wkr_model, ans):
        '''
        qstn_model: question model
        wkr_model: worker model
        ans: answer from the worker to this question
        '''
        qstn_model.ans_lt.append([wkr_model, ans])
        ans_num = len(qstn_model.ans_lt)
        qstn_model.true_prob = self.prob_strategy_gamma(qstn_model.true_prob, wkr_model.gamma, ans)
        
        if qstn_model.qstn_result == -1 and ans_num >= self.wkr_update_thres:
            if qstn_model.true_prob > 0.5:
                qstn_model.qstn_result = 1
            else:
                qstn_model.qstn_result = 0
                
            if qstn_model.contributor != None:
                cfd_arr = qstn_model.contributor.confidence_array
                cfd_arr[0] += (1 - qstn_model.true_prob)
                cfd_arr[1] += qstn_model.true_prob
                qstn_model.contributor.confidence = cfd_arr[1] / (cfd_arr[0] + cfd_arr[1])
                
            ans_lt = qstn_model.ans_lt
            for j in range(ans_num):
                self.update_wkr_model(qstn_model.true_prob, ans_lt[j][0], ans_lt[j][1])


    def update_wkr_model(self, true_prob, wkr_model, ans):
        """
        true_prob: the probability that the question's answer is true
        wkr_model: worker model
        ans: answer from the worker to this question
        """
        mat = wkr_model.confusion_matrix       
        #ans = 0 or 1, updating worker_model confusion_matrix
        mat[ans][0] += (1 - true_prob)
        mat[ans][1] += true_prob
        
        # update verifier
        wkr_model.gamma = (mat[0][0] + mat[1][1]) / (mat[0][0] + mat[1][1] + mat[0][1] + mat[1][0])
        

    def prob_strategy_gamma(self, true_prob, gamma, ans):
        '''
        true_prob: the probability that the question's answer is true
        gamma: worker's accuracy
        ans: answer from the worker to this question
        '''
        if ans == 1:
            return (true_prob * gamma) / (true_prob * gamma + (1 - true_prob) * (1 - gamma))
        else:
            return (true_prob * (1 - gamma)) / (true_prob * (1 - gamma) + (1 - true_prob) * gamma)

def test_sequence():     
    sys = INQUIRE()
    w0 = sys.WorkerModel(0)
    q1 = sys.QuestionModel(1, w0, w0.confidence)
    
    worker_lt = 100 * [None]
    for i in range(100):
        worker_lt[i] = sys.WorkerModel(i)
    
    for i in range(6):
        sys.update_qstn_model(q1, worker_lt[i], 1)
    sys.update_qstn_model(q1, worker_lt[6], 0)
    
    print(w0.confidence, w0.confidence_array, q1.true_prob)
    
    
