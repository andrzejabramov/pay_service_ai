import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation } from "@tanstack/react-query";
import { openapiRegisterApiV1AuthRegisterPostMutation } from "@/api/generated/@tanstack/react-query.gen";
import { Button } from "@/components/ui/button";
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
import { Link, useNavigate } from "react-router-dom";

const registerSchema = z
  .object({
    second_login: z
      .string()
      .min(3, "Минимум 3 символа")
      .max(64, "Максимум 64 символа"),
    phone: z
      .string()
      .min(10, "Минимум 10 символов")
      .max(20, "Максимум 20 символов"),
    email: z.string().email("Некорректный email").optional().or(z.literal("")),
    password: z.string().min(8, "Минимум 8 символов"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Пароли не совпадают",
    path: ["confirmPassword"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const mutation = useMutation({
    ...openapiRegisterApiV1AuthRegisterPostMutation(),
    onSuccess: () => {
      alert("Регистрация успешна! Теперь войдите в систему.");
      navigate("/login");
    },
    onError: (error: any) => {
      console.error("Registration failed:", error);
      const errorMsg = error?.response?.data?.detail || "Ошибка регистрации";
      alert(`Ошибка: ${JSON.stringify(errorMsg)}`);
    },
  });

  const onSubmit = (data: RegisterFormData) => {
    const { confirmPassword, ...payload } = data;
    // Отправляем на бэкенд
    mutation.mutate({
      body: {
        ...payload,
        email: payload.email || undefined,
        group_names: ["admin"], // Временно даем роль admin
      },
    });
  };

  return (
    <Card className="w-[400px] mx-auto mt-10">
      <CardHeader>
        <CardTitle>Регистрация в PayServices</CardTitle>
        <CardDescription>
          Создайте новый аккаунт для доступа к системе.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="grid gap-4">
          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="second_login">Логин</Label>
            <Input
              id="second_login"
              {...register("second_login")}
              disabled={mutation.isPending}
            />
            {errors.second_login && (
              <span className="text-red-500 text-sm mt-1">
                {errors.second_login.message}
              </span>
            )}
          </div>

          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="email">Email (опционально)</Label>
            <Input
              id="email"
              type="email"
              {...register("email")}
              disabled={mutation.isPending}
            />
            {errors.email && (
              <span className="text-red-500 text-sm mt-1">
                {errors.email.message}
              </span>
            )}
          </div>

          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="phone">Телефон (+7...)</Label>
            <Input
              id="phone"
              placeholder="+79999999999"
              {...register("phone")}
              disabled={mutation.isPending}
            />
            {errors.phone && (
              <span className="text-red-500 text-sm mt-1">
                {errors.phone.message}
              </span>
            )}
          </div>

          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="password">Пароль</Label>
            <Input
              id="password"
              type="password"
              {...register("password")}
              disabled={mutation.isPending}
            />
            {errors.password && (
              <span className="text-red-500 text-sm mt-1">
                {errors.password.message}
              </span>
            )}
          </div>

          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="confirmPassword">Подтвердите пароль</Label>
            <Input
              id="confirmPassword"
              type="password"
              {...register("confirmPassword")}
              disabled={mutation.isPending}
            />
            {errors.confirmPassword && (
              <span className="text-red-500 text-sm mt-1">
                {errors.confirmPassword.message}
              </span>
            )}
          </div>

          <Button
            type="submit"
            className="w-full mt-2"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? "Регистрация..." : "Зарегистрироваться"}
          </Button>
        </form>
      </CardContent>
      <CardFooter className="justify-center">
        <p className="text-sm text-muted-foreground">
          Уже есть аккаунт?{" "}
          <Link to="/login" className="underline hover:text-primary">
            Войти
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}
