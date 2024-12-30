from .models import Announcement , ShortCut 
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny , IsAdminUser , IsAuthenticated
from .serializers import AnnouncementSerializer , ShortCutSerializer 
from rest_framework.response import Response
from stock_affairs.permission import IsShareholder , IsPrecedence , IsUnderwriting



class AnnouncementView(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class ShortCutView(viewsets.ModelViewSet):
    queryset = ShortCut.objects.all()
    serializer_class = ShortCutSerializer
    permission_classes = [AllowAny] 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
    


# menu view
class MenuView(APIView):
    permission_classes = [IsAuthenticated]


    def menu_stock_affairs(self, request):
        main = {'title': 'امور سهام','path': ''}
        sub_menu = []

        if IsShareholder().has_permission(request, self) or request.user.is_staff:
            sub_menu.append({'title': 'سهام','path': '/shareholders/'})

        if IsPrecedence().has_permission(request, self) or request.user.is_staff:
            sub_menu.append({'title': 'حق تقدم','path': '/precendence/'})

        if IsUnderwriting().has_permission(request, self) or request.user.is_staff:
            sub_menu.append({'title': 'پذیره نویسی','path': '/underwriting/'})

        if len(sub_menu)>0:
            main['sub_menu'] = sub_menu
            return main
        else:
            return None

    def menu_correspondence(self, request):
        return {'title': 'مکاتبات', 'path': '/correspondence/'}
    
    def menu_positions(self, request):
        if request.user.is_staff:
            return {'title': 'نقش‌ها', 'path': '/positions/'}
        else:
            return None
        
    def menu_permissions(self, request):
        if request.user.is_staff:
            return {'title': 'دسترسی ها', 'path': '/permissions/'}
        else:
            return None

    def menu_groups(self, request):
        if request.user.is_staff:
            return {'title': 'گروه ها', 'path': '/groups/'}
        else:
            return None
    def menu_companies(self, request):
        main = {'title': 'شرکت ها','path': ''}
        sub_menu = []

        if request.user.is_staff:
            sub_menu.append({'title': 'ایجاد شرکت ها ', 'path': '/companies/create/'})

        if request.user.is_authenticated:
            sub_menu.append({'title': 'لیست شرکت ها ', 'path': '/companies/table/'})

        if len(sub_menu)>0:
            main['sub_menu'] = sub_menu
            return main
        
        else:
            return None
    def get(self, request):
        self.menu_items = []
        # home
        home = {
            'title': 'خانه',
            'path': '/',
        }
        self.menu_items.append(home)
        stock_affairs = self.menu_stock_affairs(request)
        correspondence = self.menu_correspondence(request)
        positions = self.menu_positions(request)
        permissions = self.menu_permissions(request)
        groups = self.menu_groups(request)
        companies = self.menu_companies(request)
        if stock_affairs:
            self.menu_items.append(stock_affairs)
        if correspondence:
            self.menu_items.append(correspondence)
        if positions:
            self.menu_items.append(positions)
        if permissions:
            self.menu_items.append(permissions)
        if groups:
            self.menu_items.append(groups)
        if companies:
            self.menu_items.append(companies)



        return Response(self.menu_items)
    
    

        
