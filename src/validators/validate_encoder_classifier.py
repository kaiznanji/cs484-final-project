from src.classifier import *
from src.encoder import *
from src.loader import *
from src.model import *
from src.utils import *

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
import torch
from torch.utils.data import DataLoader


def __validate_encoder_classifier__(nn_model = None, percent_tag: str = ""):

  device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
  print(device)

  set_seed()

  dataset_handler = LabeledUnlabeledMNIST()
  mnist_test = dataset_handler.mnist_test

  # If you are NOT using Windows, set NUM_WORKERS to anything you want, e.g. NUM_WORKERS = 4,
  # but Windows has issues with multi-process dataloaders, so NUM_WORKERS must be 0 for Windows.
  NUM_WORKERS = 0


  val_loader = DataLoader(mnist_test, batch_size=1, num_workers=NUM_WORKERS, shuffle=False)

  print("Loading encoder model from save...")
  encoder_model = EncoderModel(device, None)
  encoder_model.load_state_dict(torch.load(f"./saves/encoder_model_{percent_tag}.pth"))
  encoder_model = encoder_model.to(device)

  if not nn_model:
    print("Loading encoder classifier model from save...")
    encoder_classifier_model = EncoderClassifierModel(device, None)
    encoder_classifier_model.load_state_dict(torch.load(f"./saves/encoder_classifier_model_{percent_tag}.pth"))
  else:
    encoder_classifier_model = nn_model

  encoder_classifier_model = encoder_classifier_model.to(device)

  val_loss, accurate, confusion_matrix = validate_encoder_classifier(encoder_classifier_model, encoder_model, device, val_loader)

  print(f"Validation loss: {val_loss}")
  print(f"Accuracy %: {accurate * 100}%")

  disp = ConfusionMatrixDisplay(confusion_matrix=confusion_matrix, display_labels=[i for i in range(10)])
  disp.plot()
  plt.title("Encoder-Classifier Confusion Matrix")
  plt.show()


if __name__ == "__main__":
  __validate_encoder_classifier__()