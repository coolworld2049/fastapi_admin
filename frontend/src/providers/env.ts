import {
  LoginApi,
  Configuration,
  UsersApi,
} from "../generated";

const readApiBaseFromEnv = (): string => {
  // Get API base URL from env
  // Priority is given to same host in the browser when environment is production
  if (
    process.env.APP_ENV === "prod" &&
    !document.location.host.startsWith("localhost")
  ) {
    return `https://${document.location.host}`;
  } else if (process.env.DOMAIN && process.env.PORT) {
    return `http://${process.env.DOMAIN}:${process.env.PORT}`
  }
  return "http://localhost:8000";
};

export const readTimeZone = () => {
  return "Europe/Moscow";
};

const readAccessToken = async (): Promise<string> => {
  return localStorage.getItem("token") || "";
};

export const basePath: string = readApiBaseFromEnv();

const apiConfig: Configuration = new Configuration({
  basePath,
  accessToken: readAccessToken,
});

export const authApi: LoginApi = new LoginApi(apiConfig);
export const userApi: UsersApi = new UsersApi(apiConfig);
