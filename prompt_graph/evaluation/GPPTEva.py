import torchmetrics
import torch

def GPPTEva(data, idx_test, gnn, prompt, num_class, device):
    # gnn.eval()
    prompt.eval()
    accuracy = torchmetrics.classification.Accuracy(task="multiclass", num_classes=num_class).to(device)
    macro_f1 = torchmetrics.classification.F1Score(task="multiclass", num_classes=num_class, average="macro").to(device)
    auroc = torchmetrics.classification.AUROC(task="multiclass", num_classes=num_class).to(device)
    auprc = torchmetrics.classification.AveragePrecision(task="multiclass", num_classes=num_class).to(device)

    accuracy.reset()
    macro_f1.reset()
    auroc.reset()
    auprc.reset()

    node_embedding = gnn(data.x, data.edge_index)
    out = prompt(node_embedding, data.edge_index)
    pred = out.argmax(dim=1)  
    
    acc = accuracy(pred[idx_test], data.y[idx_test])
    f1 = macro_f1(pred[idx_test], data.y[idx_test])
    roc = auroc(out[idx_test], data.y[idx_test]) 
    prc = auprc(out[idx_test], data.y[idx_test]) 
    return acc.item(), f1.item(), roc.item(),prc.item()

def GPPTGraphEva(loader, gnn, prompt, num_class, device):
    # batch must be 1
    prompt.eval()
    accuracy = torchmetrics.classification.Accuracy(task="multiclass", num_classes=num_class).to(device)
    macro_f1 = torchmetrics.classification.F1Score(task="multiclass", num_classes=num_class, average="macro").to(device)
    auroc = torchmetrics.classification.AUROC(task="multiclass", num_classes=num_class).to(device)
    auprc = torchmetrics.classification.AveragePrecision(task="multiclass", num_classes=num_class).to(device)

    
    accuracy.reset()
    macro_f1.reset()
    auroc.reset()
    auprc.reset()
    with torch.no_grad(): 
        for batch in loader: 
            batch=batch.to(device)              
            node_embedding = gnn(batch.x,batch.edge_index)
            out = prompt(node_embedding, batch.edge_index)

            # 找到每个预测中概率最大的索引（类别）
            predicted_classes = out.argmax(dim=1)

            # 统计每个类别获得的票数
            votes = predicted_classes.bincount(minlength=out.shape[1])

            # 找出票数最多的类别
            pred = votes.argmax().item()

            # correct += int((pred == batch.y).sum())  
            acc = accuracy(pred, batch.y)
            ma_f1 = macro_f1(pred, batch.y)
            roc = auroc(out, batch.y)
            auprc(out, batch.y)
    acc = accuracy.compute()
    ma_f1 = macro_f1.compute()
    roc = auroc.compute()
    prc = auprc.compute()
       
    return acc.item(), ma_f1.item(), roc.item(), prc.item()