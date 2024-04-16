from typing import List

import numpy as np
from sklearn import mixture
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data


class MyGaussianMixture(object):
  def __init__(self):
    self.mixture = mixture.GaussianMixture(n_components=10, warm_start=True)
    self.datapoints = None

  def clear(self):
    self.datapoints = None

  def fit(self, data: torch.Tensor):
    points = data.cpu().detach().numpy()
    if self.datapoints is None:
      self.datapoints = points
    else:
      self.datapoints = np.append(self.datapoints, points, axis=0)
    
    self.mixture.fit(self.datapoints)

  def predict_one(self, point: torch.Tensor):
    return self.mixture.predict_proba(point.cpu().detach().numpy()[np.newaxis, :])

  def predict_many(self, points: torch.Tensor):
    return self.mixture.predict_proba(points.cpu().detach().numpy())


def get_optimizer(net: nn.Module, lr: float):
    optimizer = optim.Adam(net.parameters(), lr=lr)
    return optimizer
  
  
def train_model(
    model: nn.Module,
    device: torch.device,
    train_loader: torch.utils.data.DataLoader,
    optimizer: torch.optim.SGD,
    loss_graph: List[float],
    print_losses: bool = True
):
  model.train()

  for batch_id, (data, target) in enumerate(train_loader):
    data = data.to(device)
    target = target.to(device)

    optimizer.zero_grad()
    loss = model(data, target)
    loss_graph.append(loss.item())
    loss.backward()
    optimizer.step()

    if print_losses:
      print(loss_graph[-1])

  return loss


def validate_model(
    model: nn.Module,
    device: torch.device,
    val_loader: torch.utils.data.DataLoader
):
  val_loss = 0
  accurate = 0

  confusion_matrix = np.zeros((10, 10))

  model.train(False)

  with torch.no_grad():
      for batch_id, (data, target) in enumerate(val_loader):
        data = data.to(device)
        target = target.to(device)

        softmax_outputs = model(data)
        softmax_outputs = torch.from_numpy(softmax_outputs).to(device)
        val_loss += nn.CrossEntropyLoss()(softmax_outputs, target).item()
        prediction = softmax_outputs.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
        accurate += prediction.eq(target.view_as(prediction)).sum().item()

        for label, pred in zip(target, prediction):
          confusion_matrix[label, pred] += 1

  val_loss /= len(val_loader.dataset)
  accurate /= len(val_loader.dataset)
  return val_loss, accurate, confusion_matrix
