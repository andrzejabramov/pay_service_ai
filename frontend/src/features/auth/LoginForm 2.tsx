import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { openapiLoginApiV1AuthLoginPostMutation } from "@/api/generated/@tanstack/react-query.gen";
import { Button } from "@/components/ui/button";
import { Link, useNavigate } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";

const loginSchema = z.object({
  login: z.string().min(3, "Минимум 3 символа").max(64, "Максимум 64 символа"),
  password: z.string().min(8, "Минимум 8 символов"),
});

type LoginFormData = z.infer<typeof loginSchema>;

export function LoginForm() {
  const { setAccessToken, setUser } = useAuthStore();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    watch, // <-- Добавили watch для отладки
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  // Смотрим, что форма "видит" в поле login в реальном времени
  const currentLoginValue = watch("login");

  const mutation = useMutation({
    ...openapiLoginApiV1AuthLoginPostMutation(),
    onSuccess: (response) => {
      console.log("Успешный вход:", response);
      setAccessToken(response.data.access_token);
      setUser({
        id: "temp-id",
        login: currentLoginValue || "user",
        groups: ["admin"],
      });
      navigate("/");
    },
    onError: (error: any) => {
      console.error("Ошибка входа:", error);
      const errorMsg =
        error?.response?.data?.detail || "Ошибка входа. Проверьте данные.";
      alert(`Ошибка: ${JSON.stringify(errorMsg)}`);
    },
  });

  const onSubmit = (data: LoginFormData) => {
    console.log("Отправляем на сервер:", data);
    mutation.mutate({
      body: {
        login: data.login,
        password: data.password,
      },
    });
  };

  return (
    <Card className="w-[350px] mx-auto mt-20">
      <CardHeader>
        <CardTitle>Вход в PayServices</CardTitle>
        <CardDescription>Введите данные для доступа к системе.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid w-full items-center gap-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="login">Логин / Email / Телефон</Label>
              <Input
                id="login"
                placeholder="andrzejvod"
                autoComplete="username"
                {...register("login")}
                disabled={mutation.isPending}
              />

              {/* ОТЛАДОЧНЫЙ ВЫВОД: покажет длину строки, которую видит форма */}
              <div className="text-xs text-gray-500 mt-1 font-mono">
                Форма видит длину:{" "}
                {currentLoginValue ? currentLoginValue.length : 0}
                <br />
                Значение: "{currentLoginValue}"
              </div>

              {errors.login && (
                <span className="text-red-500 text-sm mt-1">
                  {errors.login.message}
                </span>
              )}
            </div>

            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register("password")}
                disabled={mutation.isPending}
              />
              {errors.password && (
                <span className="text-red-500 text-sm mt-1">
                  {errors.password.message}
                </span>
              )}
            </div>
          </div>

          <CardFooter className="flex-col gap-2 pt-4 px-0">
            <Button
              type="submit"
              className="w-full"
              disabled={mutation.isPending}
            >
              {mutation.isPending ? "Вход..." : "Войти"}
            </Button>
            <p className="text-sm text-muted-foreground">
              Нет аккаунта?{" "}
              <Link to="/register" className="underline hover:text-primary">
                Зарегистрироваться
              </Link>
            </p>
          </CardFooter>
        </form>
      </CardContent>
    </Card>
  );
}
