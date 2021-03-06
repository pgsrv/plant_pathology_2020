import torch
import torchvision
from efficientnet_pytorch import EfficientNet

from models.efficientnet import EfficientNet as CustomEfficientNet
import pretrainedmodels
import timm

class PlantModel(torch.nn.Module):
    def __init__(self, backbone_name: str, pretrained: bool = True, finetune: bool = True, num_classes: int = 4, layer_freezed: int = 3):
        super().__init__()
        self.model_name = backbone_name
        self.backbone = self.build_backbone(backbone_name, pretrained, finetune, layer_freezed, num_classes)

    def forward(self, x):
        return self.backbone(x)

    def build_backbone(self, base_model_name: str, pretrained: bool, finetune: bool, layer_freezed = 3, num_classes: int = 4):
        base_model_accepted = [
            "mobilenetv2",
            "vgg16",
            "resnet18",
            "resnet50",
            "resnext50",
            "seresnext50",
            "seresnext101",
        ]

        efficientnetns = ["efficientnetnsb" + str(i) for i in range(1, 8)]
        efficientnet = ["efficientnetb" + str(i) for i in range(1, 8)]
        base_model_accepted += efficientnetns + efficientnet

        # Mobilenet v2
        if base_model_name == "mobilenetv2":
            backbone = torchvision.models.mobilenet_v2(pretrained).features
            if finetune:
                self.set_grad_for_finetunning(backbone, 7)
            num_ftrs = backbone.classifier[-1].in_features
            backbone.classifier[-1] = torch.nn.Linear(num_ftrs, num_classes)
        # VGG 16
        elif base_model_name == "vgg16":
            backbone = torchvision.models.vgg16(pretrained).features
            if finetune:
                self.set_grad_for_finetunning(backbone, 10)
            num_ftrs = backbone.classifier[-1].in_features
            backbone.classifier[-1] = torch.nn.Linear(num_ftrs, num_classes)
        # ResNet 18
        elif base_model_name == "resnet18":
            backbone = torchvision.models.resnet18(pretrained)
            if finetune:
                self.set_grad_for_finetunning(backbone, 7)
            num_ftrs = backbone.fc.in_features
            backbone.fc = torch.nn.Linear(num_ftrs, num_classes)
        # ResNet 50
        elif base_model_name == "resnet50":
            backbone = torchvision.models.resnet50(pretrained)
            if finetune:
                self.set_grad_for_finetunning(backbone, 7)
            num_ftrs = backbone.fc.in_features
            backbone.fc = torch.nn.Linear(num_ftrs, num_classes)
        # ResNext 50
        elif base_model_name == "resnext50":
            backbone = torchvision.models.resnext50_32x4d(pretrained)
            if finetune:
                self.set_grad_for_finetunning(backbone, 7)
            num_ftrs = backbone.fc.in_features
            backbone.fc = torch.nn.Linear(num_ftrs, num_classes)
        # EfficientNet
        elif base_model_name[:-1] == "efficientnetb":
            n = base_model_name[-1]
            backbone = CustomEfficientNet.from_pretrained("efficientnet-b" + str(n))
            if finetune:
                self.set_grad_for_finetunning(backbone, 3)
            num_ftrs = backbone._fc.in_features
            backbone._fc = torch.nn.Linear(num_ftrs, num_classes)
        # EfficientNet Noisy Student
        elif base_model_name[:-1] == "efficientnetnsb":
            n = base_model_name[-1]
            backbone = timm.create_model(f"tf_efficientnet_b{n}_ns", num_classes=4, pretrained=True)
            if finetune:
                self.set_grad_for_finetunning(backbone, layer_freezed)
            num_ftrs = backbone.classifier.in_features
            backbone.classifier = torch.nn.Linear(num_ftrs, num_classes)
        # SE ResNeXt50
        elif base_model_name == "seresnext50":
            backbone = pretrainedmodels.se_resnext50_32x4d()
            if finetune:
                self.set_grad_for_finetunning(backbone, 3)
            num_ftrs = backbone.last_linear.in_features
            backbone.last_linear = torch.nn.Linear(num_ftrs, num_classes)
        # SE ResNeXt101
        elif base_model_name == "seresnext101":
            backbone = pretrainedmodels.se_resnext101_32x4d()
            if finetune:
                self.set_grad_for_finetunning(backbone, 3)
            num_ftrs = backbone.last_linear.in_features
            backbone.last_linear = torch.nn.Linear(num_ftrs, num_classes)
        else:
            print("Backbone model should be one of the following list: ")
            for name in base_model_accepted:
                print("     - {}".format(name))
            raise NotImplementedError
        return backbone

    @staticmethod
    def set_grad_for_finetunning(backbone, layer_number):
        count = 0
        for child in backbone.children():
            count += 1
            if count < layer_number:
                for param in child.parameters():
                    param.requires_grad = False
